using System;
using System.Collections.Generic;
using Rhino;
using Rhino.Geometry;

namespace TFE
{
  public static class Openings
  {
    public static void GeoBaies(List<Rectangle3d> iCrv, List<double> height, double maxWidth)
    {
      UnitConverter();
      Windows.Clear();
      Doorjambs.Clear();
      Doors.Clear();
      _maxDoorWidth = maxWidth*_unitConverter;
      WindowFrames.Clear();
      Glass.Clear();
      List<double> levelHeight = new List<double>();
      levelHeight.AddRange(height);
      levelHeight.Sort();
      List<Rectangle3d> sortedRects = new List<Rectangle3d>();
      Main(iCrv, levelHeight, sortedRects);
    }

    private static double _unitConverter;
    private static double _maxDoorWidth;
    public static List<Surface> Glass = new List<Surface>();
    public static readonly List<Brep> Windows = new List<Brep>();
    public static readonly List<Brep> Doors = new List<Brep>();
    public static readonly List<Brep> Doorjambs = new List<Brep>();
    public static readonly List<Brep> WindowFrames = new List<Brep>();

    private static void Main(List<Rectangle3d> iCrv, List<double> levelHeight, List<Rectangle3d> sortedRects)
    {
      foreach (Rectangle3d crv in iCrv)
      {
        double rectCenterZ = crv.Center.Z;
        LevelIteration(levelHeight, rectCenterZ, crv, sortedRects);
      }
    }

    private static void LevelIteration(List<double> levelHeight, double rectCenterZ, Rectangle3d crv,
      List<Rectangle3d> sortedRects)
    {
      for (int k = 1; k < levelHeight.Count; k++)
      {
        if (LevelSeparation(levelHeight, rectCenterZ, crv, sortedRects, k)) break;
      }
    }

    private static bool LevelSeparation(List<double> levelHeight, double rectCenterZ, Rectangle3d crv, List<Rectangle3d> sortedRects, int k)
    {
      if (levelHeight[k] > rectCenterZ)
      {
        WindowDoorSeparation(crv, levelHeight, k, sortedRects);
        return true;
      }
      return false;
    }

    private static void WindowDoorSeparation(Rectangle3d crv, List<double> levelHeight, int k,
      List<Rectangle3d> sortedRects)
    {
      if (crv.BoundingBox.Min.Z > levelHeight[k - 1]+20*_unitConverter)
      {
        Window(crv, sortedRects);
      }
      else
      {
        Door(crv, sortedRects);
      }
    }

    private static void Door(Rectangle3d crv, List<Rectangle3d> sortedRects)
    {
      sortedRects.Add(crv);
      List<Rectangle3d> doorBoundaries = new List<Rectangle3d>();
      RectReorientation(ref crv);
      var borderSurfaces = BorderSurfaces(crv, 50, 70);
      foreach (var borderSurface in borderSurfaces)
      {
        Doorjambs.Add(borderSurface);
      }
      List<bool> split = new List<bool>();
      RectSplit(crv, doorBoundaries, split);
      for (var index = 0; index < doorBoundaries.Count; index++)
      {
        Rectangle3d doorcrv = doorBoundaries[index];
        List<Brep> portes;
        Surface vitrage;
        //Brep doorFrame;
      
      
        PorteInd(doorcrv, split[index], 30, 0, 30, 800, 40, out portes, out vitrage);
        foreach (var porte in portes)
        {
          Doors.Add(porte);
        }
        Glass.Add(vitrage);

      }
      //Porte(crv, out cadre, out portes, out vitrage, out doorCrv);
    }

    private static void Window(Rectangle3d crv, List<Rectangle3d> sortedRects)
    {
      sortedRects.Add(crv);
      //List<Rectangle3d> doorBoundaries = new List<Rectangle3d>();
      RectReorientation(ref crv);

      Rectangle3d doorCrv = crv;
      PorteInd(doorCrv, false, 0, 0, 50, 50, 50, out List<Brep> windowFrameList, out Surface dumpSurface);
      PorteInd(doorCrv, false, 50, 50, 30, 30, 40, out List<Brep> windowList, out Surface glass);
      foreach (var window in windowList)
      {
        Windows.Add(window);
      }
      Glass.Add(glass);
      foreach (var windowFrame in windowFrameList)
      {
        WindowFrames.Add(windowFrame); 
      }



    }

    private static void UnitConverter()
    {
      var unitSystem = RhinoDoc.ActiveDoc.ModelUnitSystem;
      var unitSystemHashCode = unitSystem.GetHashCode();
      switch (unitSystemHashCode)
      {
        case 2:
          _unitConverter = 1;
          break;
        case 3:
          _unitConverter = 0.1;
          break;
        case 4:
          _unitConverter = 0.001;
          break;
      }
    
    }
    private static void PorteInd(Rectangle3d doorcrv, bool split, double a, double b, double c, double d, double thickness, out List<Brep> porte, out Surface vitrage)
    {
      double e = a;
      if (split)
      {
        e = 0;
      }
      var outerFrame = OffsetRectangle(doorcrv, a, b, e);
      var innerFrame = OffsetRectangle(outerFrame, c, d, c);
      vitrage = new PlaneSurface(innerFrame.Plane, innerFrame.X, innerFrame.Y);
    
      var door = BrepOffset(outerFrame, innerFrame, thickness);

      porte = door;
      //borderCurveList.Add(borderCurve[0].ToNurbsCurve());
    }

    private static List<Brep> BorderSurfaces (Rectangle3d doorcrv,double a, double c)
    {
      List<Line> borderCurve = Border(doorcrv);
      var outerFrame = OffsetRectangle(doorcrv, a, 0, a);
      List<Line> innerBorderCurve = Border(outerFrame);
      List<Brep> borderSurfaces = new List<Brep>();
      for (var index = 0; index < borderCurve.Count; index++)
      {
        var outerLine = borderCurve[index].ToNurbsCurve();
        var innerLine = innerBorderCurve[index].ToNurbsCurve();
        Surface borderSurface = NurbsSurface.CreateRuledSurface(outerLine, innerLine);
        Brep borderBrep = Brep.CreateFromOffsetFace(borderSurface.ToBrep().Faces[0], c*_unitConverter, 0.1*_unitConverter, true, true);
        borderSurfaces.Add(borderBrep);
      }

      return borderSurfaces;
    }

    private static List<Brep> BrepOffset(Rectangle3d outerFrame, Rectangle3d innerFrame, double a)
    {
      var outerFramelines = outerFrame.ToPolyline().GetSegments();
      var innerFramelines = innerFrame.ToPolyline().GetSegments();
      List<Brep> doorList = new List<Brep>();
      for (int i = 0; i <outerFramelines.Length; i++)
      {
        var doorBorder =NurbsSurface.CreateRuledSurface(outerFramelines[i].ToNurbsCurve(), innerFramelines[i].ToNurbsCurve()).ToBrep();
        Brep door = Brep.CreateFromOffsetFace(doorBorder.Faces[0], a*_unitConverter, 0.1, true, true);
        doorList.Add(door);
      }
      return doorList;
    }

    private static List<Line> Border(Rectangle3d doorcrv)
    {
      var polyline = doorcrv.ToPolyline();
      var exploded = polyline.GetSegments();
      List<Line> border = new List<Line>();
      foreach (var line in exploded)
      {
        var mid = (line.From + line.To) / 2;
        if (mid.Z > polyline.BoundingBox.Min.Z + 5*_unitConverter)
        {
          border.Add(line);
        }
      }

      //border.ToNurbsCurve();
      return border;
    }

    private static Rectangle3d OffsetRectangle(Rectangle3d doorcrv, double a, double b, double c)
    {
      Interval intervalX = new Interval(doorcrv.X.Min + a*_unitConverter, doorcrv.X.Max - c*_unitConverter);
      Interval intervalY = new Interval(doorcrv.Y.Min + b*_unitConverter, doorcrv.Y.Max - a*_unitConverter);
      Rectangle3d offsetRectangle = new Rectangle3d(doorcrv.Plane, intervalX, intervalY);
      return offsetRectangle;
    }

    private static void RectReorientation(ref Rectangle3d crv)
    {
      Interval intervalX;
      Interval intervalY;
      Plane plane;
      RectOrientation(crv, out intervalX, out intervalY, out plane);
      crv = new Rectangle3d(plane, intervalX, intervalY);
    }

    private static void RectSplit(Rectangle3d crv, List<Rectangle3d> doorBoundaries, List<bool>split)
    {
      if (crv.Width > _maxDoorWidth)
      {
        var doorBoundary1 = new Rectangle3d(crv.Plane, new Interval(crv.X.Min, crv.X.Mid), new Interval(crv.Y));
        doorBoundaries.Add(doorBoundary1);
        split.Add(true);
        var xDirection = crv.Plane.XAxis;
        xDirection.Reverse();
        var plane = new Plane(crv.Plane.Origin, xDirection, crv.Plane.YAxis);
        //plane.
        var doorBoundary2 = new Rectangle3d(plane, new Interval(-crv.X.Mid, -crv.X.Max), new Interval(crv.Y));
        doorBoundaries.Add(doorBoundary2);
        split.Add(true);
        return;
      }
      doorBoundaries.Add(crv);
      split.Add(false);
    }
    private static void RectOrientation(Rectangle3d crv, out Interval intervalX, out Interval intervalY, out Plane plane)
    {
      //Plane plane;
      if (crv.Plane.YAxis.IsParallelTo(Vector3d.ZAxis,Math.PI/4) == 1)
      {
        intervalX = new Interval(crv.X);
        intervalY = new Interval(crv.Y);
        plane = crv.Plane;
      }
      else
      {
        intervalX = new Interval(crv.Y);
        intervalY = new Interval(crv.X);
        plane = crv.Plane;
        plane.Flip();
      }
    }
  }
}
using System;
using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using System.Drawing;
using System.Linq;
using Rhino.Display;
using Rhino.Geometry;

using static TFE.TfeCommand;

namespace TFE
{
  public static class GenBaies
  {
    //static Random rng = new Random(SeedB);

    private static double _minOpeningWidth;
    private static double _minOpeningHeight;
    public static void PlacementBaies(Surface srf, int u, int v, double randomness, int columns, int rows, int seed, out List<Rectangle3d> oCrv, out List<List<Point3d>> xsrfPt,
      out List<List<Point3d>> srfPt, out List<List<Point3d>> openingPt, out List<double> height)
    {
      //Plane plane;
      Interval reParamInterval = new Interval(0, 1);
      srf.SetDomain(0, reParamInterval);
      srf.SetDomain(1, reParamInterval);
      srf.FrameAt(0.5, 0.5, out Plane plane);
      var min = srf.PointAt(0, 0).Z;
      var max = srf.PointAt(1, 1).Z;
      List<double> tempHeight = new List<double>();
      for (var i = 0; i < rows + 1; i++) tempHeight.Add(min + max * i / rows);
      height = tempHeight;
      Surface newSrf = (Surface) srf.DuplicateShallow();
      srfPt = new List<List<Point3d>>();
      xsrfPt = new List<List<Point3d>>();
      openingPt = new List<List<Point3d>>();
      oCrv = new List<Rectangle3d>();
      List<Rectangle3d> crv = new List<Rectangle3d>();
      Interval intervalU = new Interval(0, 2 * u);
      Interval intervalV = new Interval(0, 2 * v);
      newSrf.SetDomain(0, intervalU);
      newSrf.SetDomain(1, intervalV);
      Point3d nulPoint3d = new Point3d(0, 0, 0);

      for (var i = 0; i < 2 * v + 1; i++)
      {
        List<Point3d> srfPtList = new List<Point3d>();
        List<Point3d> xsrfPtList = new List<Point3d>();
        List<Point3d> openingPtList = new List<Point3d>();
        for (var j = 0; j < 2 * u + 1; j++)
        {
          Point3d newPt = newSrf.PointAt(j, i);
          srfPtList.Add(newPt);
          xsrfPtList.Add(nulPoint3d);
          openingPtList.Add(nulPoint3d);
        }

        openingPt.Add(openingPtList);
        srfPt.Add(srfPtList);
        xsrfPt.Add(xsrfPtList);
      }

      var seedpt = 1;
      //var tailleXMin = 0.8;
      var columnWidth = TileXSize * u / columns;
      //var tailleYMin = 0.8;
      var rowHeight = TileYSize * v / rows;
      _minOpeningWidth = Math.Min(MinOpeningWidth, columnWidth - 2 * MargeX);
      _minOpeningWidth = Math.Max(_minOpeningWidth, TileXSize);
      _minOpeningHeight = Math.Min(MinOpeningHeight, rowHeight - (UpperMargin + LowerMargin));
      _minOpeningHeight = Math.Max(_minOpeningHeight, TileYSize);
      var margeX = Math.Ceiling(MargeX / TileXSize) * columns / u;
      if (Math.Abs(margeX - 1) < 0.01)
        return;
      var upperMargin = Math.Ceiling(UpperMargin / TileYSize) * rows / v;
      var lowerMargin = Math.Ceiling(LowerMargin / TileYSize) * rows / v;
      var minWidth = Math.Ceiling(MinOpeningWidth / TileXSize) * columns / u;
      var minHeight = Math.Ceiling(MinOpeningHeight / TileYSize) * rows / v;
      //Gen domaine de baies 
      
      List<int> numbers = new List<int>(Enumerable.Range(0, columns));
      //numbers.Shuffle();
      Random rng = new Random(SeedB);
      var n = numbers.Count;
      while (n > 1)
      {
        n--;
        var k = rng.Next(n + 1);
        (numbers[k], numbers[n]) = (numbers[n], numbers[k]);
      }

      List<int> doorList = new List<int>();
      for (var i = 0; i < DoorNumber; i++) doorList.Add(numbers[i]);
      for (var i = 0; i < columns; i++)
      {
        for (var j = 0; j < rows; j++)
        {
          Random rand = new Random(seedpt * seed);
          seedpt++;
          var randx1 = margeX + rand.NextDouble() * (1 - 2 * margeX - minWidth) * randomness;
          if (randx1 < margeX)
            randx1 = margeX;
          var randy1 = lowerMargin + rand.NextDouble() * (1 - lowerMargin - upperMargin - minHeight) * randomness;
          if (randy1 < lowerMargin)
            randy1 = lowerMargin;
          if (j == 0 && doorList.Contains(i) && randy1<1)
            randy1 = 0;
          var randx2 = 1 - margeX - rand.NextDouble() * (1 - randx1 - margeX) * randomness;
          var randy2 = 1 - upperMargin - rand.NextDouble() * (1 - randy1 - upperMargin) * randomness;
          var x1 = Conversion(randx1, i, columns, u);
          x1 = Math.Ceiling(x1);
          var y1 = Conversion(randy1, j, rows, v);
          y1 = Math.Ceiling(y1);
          var x2 = Conversion(randx2, i, columns, u);
          x2 = Math.Floor(x2);
          var y2 = Conversion(randy2, j, rows, v);
          y2 = Math.Floor(y2);

          x1 *= 2;
          x2 *= 2;
          y1 *= 2;
          y2 *= 2;
          var minOpeningHeight = MinOpeningHeight;
          if (j == 0 && doorList.Contains(i))
            minOpeningHeight = 2;
          var offsetX = Math.Ceiling(MinOpeningWidth / TileXSize) * 2;
          var deltaX = x2 - x1;
          var offsetY = Math.Ceiling(minOpeningHeight / TileYSize) * 2;
          var deltaY = y2 - y1;
          if (((int) x1 == (int) x2) | (deltaX < offsetX))
            x2 += offsetX - deltaX;
          x2 = Math.Min(x2, srfPt[0].Count - 1);
          if (((int) y1 == (int) y2) | (deltaY < offsetY))
            y2 += offsetY - deltaY;
          y2 = Math.Min(y2, srfPt.Count - 1);
          Point3d cornerA = srfPt[(int) y1][(int) x1];
          Point3d cornerB = srfPt[(int) y2][(int) x2];
          Rectangle3d rect = new Rectangle3d(plane, cornerA, cornerB);
          crv.Add(rect);
          for (var k = (int) y1 + 1; k < y2; k++)
          {
            for (var l = (int) x1 + 1; l < x2; l++) xsrfPt[k][l] = srfPt[k][l];
          }

          for (var k = (int) y1; k < y2; k++) //col gauche
            openingPt[k][(int) x1] = srfPt[k][(int) x1];
          for (var k = (int) x1 + 1; k < x2; k++) //col gauche
            openingPt[(int) y1][k] = srfPt[(int) y1][k];
        }
      }

      //openingPt = openingPt;
      //xsrfPt = xsrfPt;
      //_srfPt = srfPt;
      //plane = plane;
      oCrv = crv;
    }

    public static double Conversion(double rand, int i, int size, int div)
    {
      //var normalized = reducedInterval.ParameterAt(rand);
      var t0 = i / (double) size * div;
      var t1 = (i + 1) / (double) size * div;
      Interval subInterval = new Interval(t0, t1);
      var final = subInterval.ParameterAt(rand);
      return final;
    }
  }

  public class BaiesConduit : DisplayConduit
  {
    public List<Brep> Breps { get; set; }

    protected override void CalculateBoundingBox(CalculateBoundingBoxEventArgs bbe)
    {
      base.CalculateBoundingBox(bbe);
      List<Brep> breps = Breps;
      foreach (Brep brep in breps)
      {
        BoundingBox bb = brep.GetBoundingBox(false);
        bbe.IncludeBoundingBox(bb);
      }
    }

    protected override void DrawOverlay(DrawEventArgs drawe)
    {
      base.DrawOverlay(drawe);
      foreach (Brep brep in Breps) drawe.Display.DrawBrepWires(brep, Color.Blue);
    }
  }
}
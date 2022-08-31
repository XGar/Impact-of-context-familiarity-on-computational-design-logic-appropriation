using System;
using System.Collections.Generic;
using Rhino.DocObjects;
using Rhino.Geometry;
using static TFE.TfeCommand;

namespace TFE
{
  public static class Functions
  {
    public static double _tx;
    public static double _ty;
    public static void Divisions(Surface srf, out int divX, out int divY)
    {
      Interval reparamInterval = new Interval(0, 1);
      srf.SetDomain(0, reparamInterval);
      srf.SetDomain(1, reparamInterval);
      srf.FrameAt(0.5, 0.5, out Plane orientationPlane);
      Point3d corner1 = srf.PointAt(0, 0);
      Point3d corner2 = srf.PointAt(1, 1);
      BoundingBox srfBbox = srf.GetBoundingBox(orientationPlane);
      _ty = corner2.Z - corner1.Z;
      corner1.Z = 0;
      corner2.Z = 0;
      _tx = corner1.DistanceTo(corner2);

      TileXSize = _tx / (Math.Round(_tx*0.5 / TileXSize)*2);
      TileXSize = Math.Round(TileXSize, 2);
      TileYSize = _ty / (Math.Round(_ty*0.5 / TileYSize)*2);
      TileYSize = Math.Round(TileYSize, 2);
      int tempdivX = (int) (_tx / TileXSize)/2;
      divX = tempdivX * 2 ;
      int tempdivY = (int) (_ty / TileYSize)/2;
      divY = tempdivY * 2;

    }
  }
}
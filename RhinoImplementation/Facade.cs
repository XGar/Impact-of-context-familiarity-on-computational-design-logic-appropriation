using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using Rhino.Display;
using Rhino.Geometry;

namespace TFE
{
  //TODO Maybe rework the iteration length for each size
  public static class Facade
  {
    //public static Point3d[,] Pts = new Point3d[0,0];
    private static List<int> _indexList = new List<int>();
    private static int _seed;
    private static int _maxX;
    private static int _maxY;
    public static Plane Pln = new Plane();
    public static Point3d Nul = new Point3d(0, 0, 0);
    public static void Cladding(List<List<Point3d>> iPoints, List<List<Point3d>> exPoints, List<List<Point3d>> openingPts, Point3d nullPoint, int seed, int maxX, int maxY, out List<Rectangle3d> claddingRects) 
    {
      _indexList.Clear();
      // ReSharper disable once PossibleLossOfFraction
      double limit = iPoints[0].Count / 2;
      _maxX = Math.Min(maxX,(int)Math.Floor(limit));
      List<List<Point3d>> pts = new List<List<Point3d>>();
      pts.AddRange(iPoints);
      List<List<Point3d>> xPts = new List<List<Point3d>>();
      xPts.AddRange(exPoints);
      Nul = nullPoint;
      _seed = seed;
      for (var i = 0; i < iPoints.Count-1; i++) //Pts
      {
        for (var j = 0; j < iPoints[i].Count-1;j++)
        {
          if ((exPoints[i][j] == Nul))// | )
          {
            if (((i % 2) == 0) && ((j % 2) == 0))
            {
              _indexList.Add((i * 1000 + j));
            }
          }
          if ((openingPts[i][j] != Nul))// | )
          {
            if (((i % 2) == 0) && ((j % 2) == 0))
            {
              if (_indexList.Contains(i * 1000 + j))
                _indexList.Remove((i * 1000 + j));
            }
          }
        }
      }

      List<Rectangle3d> oRect = new List<Rectangle3d>();
      oRect.Clear();
      _maxY = Math.Min(maxY,pts.Count);
      //_maxX 
      for (int j = _maxX, i = _maxY, m = i*j; m >1; )
      {
        Rectangle(i*2, j*2, ref pts, ref xPts, ref oRect, ref _indexList);
        if (i >1) 
          Rectangle((i-1)*2, j*2, ref pts, ref xPts, ref oRect, ref _indexList); 
        if (j >1)  
          Rectangle(i*2, (j-1)*2, ref pts, ref xPts, ref oRect, ref _indexList); 
        if (i >1)
          --i; 
        if (j >1)
          --j; 
        m = i * j;
      }
      foreach (var id in _indexList)
      {
        int id1 = id / 1000;
        int id2 = id - id1 * 1000;
        Plane rPlane = new Plane(pts[id1 + 2][id2], pts[id1][id2], pts[id1 + 2][id2 + 2]);
        var rec = new Rectangle3d(rPlane, pts[id1][id2], pts[id1 + 2][id2 + 2]);
        oRect.Add(rec);
      }
      claddingRects = oRect;
    }
    private static Rectangle3d CheckRectangle(int x, int y, int[] index,List<List<Point3d>> pts, ref List<List<Point3d>> xPts, ref int iter, ref List<int> indexList, ref List<int> tempList)
    {
      var insidePtsIdx = InsidePts(x, y, index);
      var perimeterIdx = PerimeterPts(x, y, index);
      bool test = false;
      Rectangle3d rect = new Rectangle3d();
      foreach (List<int> idx in perimeterIdx)
      {
        Point3d inPt = xPts[idx[0]][idx[1]];
        test = !(inPt.Equals(Nul));
        if (!test) continue;
        foreach (var removeId in from idx2 in perimeterIdx where idx2[0] % 2 == 0 && idx2[1] % 2 == 0 select idx2[0] * 1000 + idx2[1])
        {
          if (tempList.Contains(removeId))
          {tempList.Remove(removeId);}
        }
        break;
      }
      if (!test)
      {
        foreach (List<int> idx in insidePtsIdx)
        {
          var inPt = xPts[idx[0]][idx[1]];
          test = !(inPt.Equals(Nul));
          if (test)
          {
            if (tempList.Contains(idx[0] * 1000 + idx[1]))
              tempList.Remove(idx[0] * 1000 + idx[1]); 
            break;
          }
        }
      }
      if (test)
      {
        iter++;
      }
      else
      {
        Point3d cptA = pts[index[0]][index[1]];
        Point3d cptB = pts[(index[0] + x)][(index[1] + y)];
        var cptC = pts[index[0]][index[1] + y];
        var plane = new Plane(cptC, cptA, cptB);
        if (cptA != cptB)
        {
          Rectangle3d r = new Rectangle3d(plane, cptA, cptB);
          rect = r;
        }
        for (int i = 1; i < (x) ;i++)//Left column 
        {
          List<int> idx = new List<int>
          {
            index[0] + i,
            index[1]
          };
          if ((idx[0] % 2 == 0) && (idx[1] % 2 == 0))
          {
            indexList.Remove(idx[0] * 1000 + idx[1]);
            tempList.Remove(idx[0] * 1000 + idx[1]);

          }
        }
        for (int i = 1; i < (y) ;i++)//Bottom Row 
        {
          List<int> idx = new List<int>
          {
            index[0],
            index[1] + i
          };
          if ((idx[0] % 2 == 0) && (idx[1] % 2 == 0))
          {
            indexList.Remove(idx[0] * 1000 + idx[1]);
            tempList.Remove(idx[0] * 1000 + idx[1]);

          }
        }
        foreach (List<int> idx in insidePtsIdx)
        {
          if ((idx[0] % 2 == 0) && (idx[1] % 2 == 0))
          {
            indexList.Remove(idx[0] * 1000 + idx[1]);
            tempList.Remove(idx[0] * 1000 + idx[1]);
          }
          xPts[idx[0]][idx[1]] = pts[idx[0]][idx[1]];
        }
      }
      return rect;
    }
    private static List<List<int>> InsidePts(int x, int y, IReadOnlyList<int> index)
    {
      List<List<int>> insidePtsIndex = new List<List<int>>();
      for (int i = 1; i < x;i++)
      {

        for (int j = 1;j < y;j++)
        {

          List<int> idx = new List<int>
          {
            index[0] + i,
            index[1] + j
          };
          insidePtsIndex.Add(idx);
        }
      }
      return insidePtsIndex;
    }
    private static List<List<int>> PerimeterPts(int x, int y, IReadOnlyList<int> index)
    {
      List<List<int>> insidePointsIndex = new List<List<int>>();
      for (var i = 0; i < (x + 1) ;i++) //left column 
      {
        List<int> idx = new List<int>
        {
          index[0] + i,
          index[1]
        };
        insidePointsIndex.Add(idx);
      }
      for (int i = 0; i < (x + 1);i++) //right column
      {
        List<int> idx = new List<int>
        {
          index[0] + i,
          index[1] + y
        };
        insidePointsIndex.Add(idx);
      }
      for (var i = 1; i < y;i++)  // Bottom row
      {
        List<int> idx = new List<int>
        {
          index[0],
          index[1] + i
        };
        insidePointsIndex.Add(idx);
      }
      for (var i = 1; i < y ;i++) // Top row
      {
        List<int> idx = new List<int>
        {
          index[0] + x,
          index[1] + i
        };
        insidePointsIndex.Add(idx);
      }

      return insidePointsIndex;
    }
    private static void Rectangle (int i, int j, ref List<List<Point3d>> pts, ref List<List<Point3d>> xPts, ref List<Rectangle3d> oRect, ref List<int> indexList)
    {
      int iteration = 0;
      List<int> tempList = new List<int>();
      var x = pts[0].Count;
      var y = pts.Count;
      tempList.AddRange(indexList);
      var rand = new Random(_seed);
      int listLength = tempList.Count;
      while ((iteration < ((2) + listLength * ((_maxX*_maxY+1) - (j / 2) *( i / 2)) * 1)) && (listLength > 0))
      {
        int idx = rand.Next(((y-i)/2)+1)*2;
        int idy = rand.Next(((x-j)/2)+1)*2;
        var temp = (idx * 1000) + idy;
        if (tempList.Contains(temp))
          tempList.Remove(temp);
        int id1 = idx;
        int id2 = idy;
        int[] index = {id1,id2};
        Rectangle3d rect = CheckRectangle(i, j, index, pts, ref xPts, ref iteration, ref indexList, ref tempList);
        if (rect.Height > 0)
        {
          indexList.Remove(temp);
          //TODO maybe remove points from temp list that cant be in: -i left and -j under
          oRect.Add(rect);
        }
        _seed++;
        listLength = tempList.Count;
      }
    } 
  }
  public class FacadeConduit : DisplayConduit
  {
    public List<Rectangle3d> Rects { get; set; }
    protected override void CalculateBoundingBox(CalculateBoundingBoxEventArgs bbe)
    {
      base.CalculateBoundingBox(bbe);
      List<Rectangle3d> rectangle3ds = Rects;
      foreach (var rectangle3d in rectangle3ds)
      {
        BoundingBox bb = rectangle3d.BoundingBox;
        bbe.IncludeBoundingBox(bb);
      }
    }

    protected override void DrawOverlay(DrawEventArgs drawe)
    {
      base.DrawOverlay(drawe);
      foreach (var rectangle3d in Rects)
      {
        drawe.Display.DrawCurve(rectangle3d.ToPolyline().ToPolylineCurve(),Color.Blue);
      }
    }
  }
}
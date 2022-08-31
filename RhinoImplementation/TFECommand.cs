using System;
using System.Collections;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using Rhino;
using Rhino.Commands;
using Rhino.DocObjects;
using Rhino.Geometry;
using Rhino.Input;
using Rhino.Input.Custom;
using static TFE.GenBaies;
using static TFE.Openings;
using static TFE.Functions;
using static TFE.Facade;

namespace TFE
{
  public class TfeCommand : Command
  {
    ///<summary>The only instance of this command.</summary>
    public static TfeCommand Instance
    {
      get; private set;
    }

    ///<returns>The command name as it appears on the Rhino command line.</returns>
    public override string EnglishName
    {
      get { return "Facade"; }
    }

    private int _indexSize;
    public static double TileXSize = 0.3;
    public static double TileYSize = 0.3;
    private int _divX = 12;
    private int _divY = 12;
    private int _maxX = 3;
    private int _maxY = 3;
    public static double MargeX = 0.2;
    public static double UpperMargin = 0.2;
    public static double LowerMargin = 0.8;
    public static double MinOpeningWidth = 0.8;
    public static double MinOpeningHeight = 0.8;
    public static int DoorNumber = 1;
    private int _columns = 2;
    private int _rows = 2;
    private int _seed = 1;
    public static int SeedB = 1;
    private double _variability = 0.2;
    private List<Rectangle3d> _oCrv;
    private List<List<Point3d>> _srfPt;
    private List<List<Point3d>> _xsrfPt;
    private List<Brep> _previewGeom;
    private List<List<Point3d>> _openingPt;
    private readonly List<double> _oldParameters = new List<double>();
    private List<Rectangle3d> _cladRects;
    private string _srfName;
    protected override Result RunCommand(RhinoDoc doc, RunMode mode)
    {
      _oldParameters.Clear();
      GetObject getSurfaceAction = new GetObject();
      getSurfaceAction.EnablePressEnterWhenDonePrompt(true);
      getSurfaceAction.GeometryFilter = ObjectType.Surface;
      getSurfaceAction.SubObjectSelect = true;
      getSurfaceAction.BottomObjectPreference = true;
      getSurfaceAction.SetCommandPrompt("Please select the target surface");
      GetResult getRcSrf = getSurfaceAction.Get();
      Surface srf = getSurfaceAction.Object(0).Surface();
      if (getRcSrf == GetResult.Nothing)
      {
        doc.Views.Redraw();
      }
      else if (getRcSrf == GetResult.Object)
      {
        srf = getSurfaceAction.Object(0).Surface();
        var id  = getSurfaceAction.Objects()[0].ObjectId;
        _srfName = RhinoDoc.ActiveDoc.Objects.FindId(id).Name;
        doc.Views.Redraw();
      }
      var optionMenu = new GetOption();
      optionMenu.AddOption("Maillage");
      optionMenu.AddOption("Baies");
      optionMenu.SetCommandPrompt("");
      optionMenu.EnableTransparentCommands(true);
      optionMenu.AcceptEnterWhenDone(true);
      FacadeConduit facadeConduit = new FacadeConduit();
      BaiesConduit bConduit = new BaiesConduit();
      bConduit.Enabled = true;
      facadeConduit.Enabled = true;
      Menu:
      doc.Views.RedrawEnabled = true; 
      for (;;)
      {
        facadeConduit.Enabled= false;
        bConduit.Enabled = false;
        doc.Views.Redraw();
        GenFacade(srf, out _cladRects);
        facadeConduit.Rects = _cladRects;
        bConduit.Breps = _previewGeom;
        facadeConduit.Enabled= true;
        bConduit.Enabled = true;
        doc.Views.Redraw();
        GetResult getRc = optionMenu.Get();
        RhinoDoc.ActiveDoc.Views.Redraw();
        if (getRc == GetResult.Nothing)
        {
          facadeConduit.Rects = _cladRects;
          bConduit.Breps = _previewGeom;
          doc.Views.Redraw();
          //break;
        }
        else if (getRc == GetResult.Option)
        {
          //HighlightSelected(selectedObjects, true);
          switch (optionMenu.OptionIndex())
          {
            case 1:
              goto Maillage;
            case 2:
              goto Baies;
                        
          }
          facadeConduit.Enabled = false;
          continue;
        }
        doc.Views.Redraw();
        facadeConduit.Enabled = false;
        bConduit.Enabled = false;
        break;
      }
      facadeConduit.Enabled = false;
      bConduit.Enabled = false;
      BakeRect(_cladRects);
      List<Brep> tileSrf = new List<Brep>();
      foreach (var crv in _cladRects)
      {
        //Random color variation ? 
        tileSrf.Add(new PlaneSurface(crv.Plane,crv.X,crv.Y).ToBrep());
      }
      BakeBrep(tileSrf);
      BakeRect(_oCrv);
      BakeBrep(_previewGeom);
      doc.Views.Redraw();
      return Result.Success;
                
      Maillage:
      using (GetInteger getOptionAction = new GetInteger())
      {
        doc.Views.Redraw();
        OptionInteger multX = new OptionInteger(_maxX, 1, 10);
        OptionInteger multY = new OptionInteger(_maxY, 1, 10);
        GenFacade(srf, out _cladRects);
        getOptionAction.SetCommandPrompt("Taille");
        getOptionAction.AddOption("X",TileXSize.ToString());
        getOptionAction.AddOption("Y", TileYSize.ToString());
        getOptionAction.AddOption("Random_Next");
        getOptionAction.AddOption("Random_Back");
        getOptionAction.AddOptionInteger("Multiple_X", ref multX);
        getOptionAction.AddOptionInteger("Multiple_Y", ref multY);
        getOptionAction.AcceptEnterWhenDone(true);
        bConduit.Breps = _previewGeom;
        bConduit.Enabled = true;
        facadeConduit.Rects = _cladRects;
        doc.Views.Redraw();
        GetResult getRc = getOptionAction.Get();
        if (getRc == GetResult.Option)
        {
          _indexSize = getOptionAction.OptionIndex();
          switch (_indexSize)
          {
            case 1:
              goto TileSize;
            case 2:
              goto TileSize;
            case 3:
            {
              //var rand = new Random();
              _seed += _columns * _rows;
              //_seed = rand.Next();
              //_seed = rand.
              doc.Views.Redraw();
              goto Maillage;
            }
            case 4:
            {
              //var rand = new Random();
              _seed -= _columns * _rows;
              //_seed = rand.Next();
              //_seed = rand.
              doc.Views.Redraw();
              goto Maillage;
            }
            case 5:
            {
              _maxX = getOptionAction.Number();
              doc.Views.Redraw();
              goto Maillage;
            }
            case 6:
            {
              _maxY = getOptionAction.Number();
              doc.Views.Redraw();
              goto Maillage;
            }
          }
        }
        goto Menu;
      }
            
      TileSize:
      Point3d pt0 = new Point3d();
      Point3d pt2= new Point3d();
      double taille;
      using (GetPoint getPointAction = new GetPoint())
      {
        getPointAction.SetCommandPrompt("Specifier Longueur ou choisir premier point de référence");
        getPointAction.AcceptNumber(true,true);
        if (getPointAction.Get() == GetResult.NoResult)
        {
          goto Maillage;
        }
        if (getPointAction.Result() == GetResult.Number)
        {
          if (getPointAction.Number() < 0.05)
          {
            RhinoApp.WriteLine("La taille selectionée est trop petite");
            goto TileSize;
          }
          taille = getPointAction.Number();
          switch (_indexSize)
          {
            case 1:
            {
              TileXSize = taille;
              goto Maillage;
            }
            case 2:
            {
              TileYSize = taille;
              goto Maillage;
            }
          }
        }

        pt0 = getPointAction.Point(); 
      }
      using (GetPoint getPointAction = new GetPoint())
      {
        getPointAction.SetCommandPrompt("Choisir deuxieme point");
        getPointAction.AcceptNumber(true,false);
        getPointAction.PermitElevatorMode(1);
        getPointAction.AcceptNothing(true);
        getPointAction.SetBasePoint(pt0, true);
        Point3d pt1 = pt0;
        getPointAction.DynamicDraw +=
          (sender, e) => e.Display.DrawLine(pt1, e.CurrentPoint, Color.DarkRed);
        if (getPointAction.Get() == GetResult.NoResult)
        {
          pt0 = new Point3d();
          goto Maillage;
        }
        if (getPointAction.Result() == GetResult.Number)
        {
          if (getPointAction.Number() < 0.01)
          {
            RhinoApp.WriteLine("La taille selectionée est trop petite");
            goto TileSize;
          }
          taille = getPointAction.Number();
          switch (_indexSize)
          {
            case 0:
            {
              TileXSize = taille;
              goto Maillage;
            }
            case 2:
            {
              TileYSize = taille;
              goto Maillage;
            }
          }
        }
        pt2 = getPointAction.Point();
      }

      var dist = pt2.DistanceTo(pt0);
      pt0 = new Point3d();
      taille = dist;
      switch (_indexSize)
      {
        case 1:
        {
          if (taille>_tx)
            goto Maillage;
          TileXSize = taille;
          goto Maillage;
        }
        case 2:
        {
          if (taille>_ty)
            goto Maillage;
          TileYSize = taille;
          goto Maillage;
        }
      }
      goto Maillage;
            
      Baies:
      GenFacade(srf, out _cladRects);
      bConduit.Breps = _previewGeom;
      bConduit.Enabled = true;
      facadeConduit.Rects = _cladRects;
      doc.Views.Redraw();
      using (GetOption getOptionAction = new GetOption())
      {
        OptionInteger rng = new OptionInteger(_rows, 1, 5);
        OptionInteger col = new OptionInteger(_columns, 1, 5);
        OptionInteger doorNumber = new OptionInteger(DoorNumber, 0, _columns);
        OptionDouble rdm = new OptionDouble(_variability, 0, 1);
        OptionDouble margeLat = new OptionDouble(MargeX, 0, 10);//revoir upperLimit
        OptionDouble margeinf = new OptionDouble(LowerMargin, 0, 10);
        OptionDouble margesup = new OptionDouble(UpperMargin, 0, 10);
        OptionDouble taillexmin = new OptionDouble(MinOpeningWidth, 0, 10);
        OptionDouble tailleymin = new OptionDouble(MinOpeningHeight, 0, 10);//revoir upperLimit
        getOptionAction.AddOptionInteger("Rangées",ref rng,"Choisir le nombre de rangées de baies voulues");
        getOptionAction.AddOptionInteger("Colonnes", ref col, "Choisir le nombre de colonnes de baies voulues");
        getOptionAction.AddOptionDouble("randomness",ref rdm);
        getOptionAction.AddOption("Random_Next");
        getOptionAction.AddOption("Random_Back");
        getOptionAction.AddOptionDouble("Marge_Laterale",ref margeLat, "Marge entre baies voisines");
        getOptionAction.AddOptionDouble("HauteurAllège",ref margeinf, "Hauteur d'allège min");
        getOptionAction.AddOptionDouble("MargeSup",ref margesup, "Marge supérieure");
        getOptionAction.AddOptionDouble("LargeurMin", ref taillexmin, "Largeur de baie minimale");
        getOptionAction.AddOptionDouble("HauteurMin", ref tailleymin, "Hauteur de baie minimale");
        getOptionAction.AddOptionInteger("NbrPorte", ref doorNumber, "Combien de portes?");
        getOptionAction.SetCommandPrompt("Baies:");
        GetResult getRc = getOptionAction.Get();
        if (getRc == GetResult.Option)
        {
          var choixIndex = getOptionAction.OptionIndex();
          switch (choixIndex)
          {
            case 1:
            {
              _rows = (int)getOptionAction.Number();
              goto Baies;
            }
            case 2:
            {
              _columns = (int)getOptionAction.Number();
              goto Baies;
            }
            case 3:
            {
              _variability = getOptionAction.Number();
              goto Baies;
            }
            case 4:
            {
              //var rand = new Random();
              SeedB++; //= rand.Next();
              doc.Views.Redraw();
              goto Baies;
            }
            case 5:
            {
              //var rand = new Random();
              --SeedB;// = rand.Next();
              doc.Views.Redraw();
              goto Baies;
            }
            case 6:
            {
              MargeX = getOptionAction.Number();
              goto Baies;
            }
            case 7:
            {
              LowerMargin = getOptionAction.Number();
              goto Baies;
            }
            case 8:
            {
              UpperMargin = getOptionAction.Number();
              goto Baies;
            }
            case 9:
            {
              MinOpeningWidth = getOptionAction.Number();
              goto Baies;
            }
            case 10:
            {
              MinOpeningHeight = getOptionAction.Number();
              goto Baies;
            }
            case 11:
            {
              DoorNumber = (int)getOptionAction.Number();
              goto Baies;
            }
          }
        }
      }
      goto Menu;
    }

    private static void BakeRect(List<Rectangle3d> cladrects)
    {
      foreach (var crv in cladrects)
      {
        var att = new ObjectAttributes();
        att.LayerIndex = RhinoDoc.ActiveDoc.Layers.CurrentLayerIndex;
        RhinoDoc.ActiveDoc.Objects.AddRectangle(crv);
      }
    }
    private static void BakeBrep(List<Brep> cladrects)
    {
      foreach (var crv in cladrects)
      {
        var att = new ObjectAttributes();
        att.LayerIndex = RhinoDoc.ActiveDoc.Layers.CurrentLayerIndex;
        RhinoDoc.ActiveDoc.Objects.AddBrep(crv);
      }
    }
    //public List<Brep> doors;
    private void GenFacade(Surface srf, out List<Rectangle3d> cladrects)
    {
      var rhinoPath = RhinoDoc.ActiveDoc.Path;
      var rhinoName = RhinoDoc.ActiveDoc.Name;
      rhinoPath = rhinoPath.TrimEnd(rhinoName.ToCharArray());
      //rhinoName = rhinoName.TrimEnd(".3dm".ToCharArray());
      rhinoName = rhinoName.Substring(0, rhinoName.Length - 4);
      //RhinoApp.WriteLine(rhinoPath);
      rhinoPath+=rhinoName+".csv";
      if (!File.Exists(rhinoPath))
      {
        string headers = "Time;" + "Object;" + "TileXSize;" + "TileYSize;" + "Variability;" + "Columns;" + "Rows;" + 
                         "MultipleX;" + "MultipleY;" + "CladdingSeed;" + "OpeningSeed;" + "MargeX;" + "UpperMargin;" + 
                         "LowerMargin;" + "MinOpeningHeight;" + "MinOpeningWidth;" + "DoorNumber" + "\n";
        File.AppendAllText(rhinoPath,headers);
        
        
      }
      var now=System.DateTime.Now;
      var test = now.Hour+":"+now.Minute+":"+now.Second+":"+now.Millisecond+";";
      
      List<double> parameters = new List<double>
      {
        TileXSize, TileYSize, _variability, _columns, _rows, _maxX, _maxY, _seed, SeedB, MargeX, UpperMargin, LowerMargin,
        MinOpeningHeight, MinOpeningWidth,DoorNumber 
      };
      if (_oldParameters.Count > 0)
      {
        int check = 1;
        for (var i = 0; i < parameters.Count; i++)
        {
          if (Math.Abs(parameters[i] - _oldParameters[i]) > 0.01)
            check = 0;
        }
        if (check == 1)
        {
          cladrects = _cladRects;
          return;
        }
      }

      test += "3." + _srfName + ";";
      _oldParameters.Clear();
      foreach (var parameter in parameters)
      {
        _oldParameters.Add(parameter);
        test+=(parameter.ToString())+";";
      }
      test += "\n";
      File.AppendAllText(rhinoPath,test);
      Divisions(srf, out _divX, out _divY);
      List<double> height; 
      PlacementBaies(srf, _divX, _divY, _variability, _columns, _rows, SeedB, out _oCrv, out _xsrfPt,
        out _srfPt, out _openingPt, out height);
      if (_oCrv.Count > 0)
      { 
        GeoBaies(_oCrv, height, 1000);
        _previewGeom = Doors;
        _previewGeom.AddRange(Doorjambs);
        _previewGeom.AddRange(Windows);
        _previewGeom.AddRange(WindowFrames);
      }
      else
      {
        _previewGeom.Clear();
      }
      Cladding(_srfPt, _xsrfPt, _openingPt, Nul, _seed, _maxX, _maxY, out cladrects);
    }

    private static void HighlightSelected(List<ObjRef> selectedObjects, bool highlight)
    {
      foreach (var selectedObject in selectedObjects)
      {
        RhinoDoc.ActiveDoc.Objects.FindId(selectedObject.ObjectId)
          .HighlightSubObject(selectedObject.GeometryComponentIndex, highlight);
      }
    }
  }

}
UNIT IdeDemo;

INTERFACE

Uses // SimForm  {type TSimWindow},
     // Preview  {var  PreviewForm},
     IdeFact  {type TLinkage},
     IdeTree  {type TElement},
     IdeDesc  {type TBasicDesc},
     IdeRun   {func FindContext},
     SimCls   {type TSimWindow},
     SimCtl   {type TSimWindow_Element};

Procedure Demo (top: TElement);
{ Create preview of a window }

IMPLEMENTATION

(********************************** DEMO **********************************)

Procedure CreateViewBranch (elem: TElement);
{ Create products  }
Var  sub: TElement;
     rel: TLinkage;
     loc: TElement;
Begin
     if a and b or not c and not d then
        a := b*c + d*e;
     if a or b then
        a := b + c * d;
     if not (a or b) then
        a := b + c * d;
     if not (a and b) then
        a := b*c + d*e;
     { create product }
     Assert (elem <> nil);
     elem.Product := elem.CreateProduct;
     Assert (elem.Product <> nil);

     { subitems }
     sub := elem.FirstElem;
     while sub <> nil do begin

        { create subitem }
        CreateViewBranch (sub);

        { link tree }
        if (elem.Product <> nil) and (sub.Product <> nil) then begin
           FindContext (elem, sub, loc, rel);
           if rel <> nil then
              rel.InsertLast (loc.Product, sub.Product);
        end;

        sub := sub.NextElem;
     end;
End;

{--------------------------------------------------------------------------}

Procedure SetupViewBranch (elem: TElement);
{ Store parameter values }
Var  sub: TElement;
     param: TParam;
Begin
     if elem.Product <> nil then begin
        param := elem.FirstParam;
        while param <> nil do begin
           param.Store (elem.Product);
           param := param.NextParam;
        end;
     end;

     { setup subitems }
     sub := elem.FirstElem;
     while sub <> nil do begin
        SetupViewBranch (sub);
        sub := sub.NextElem;
     end;
End;

{--------------------------------------------------------------------------}

Procedure Demo (top: TElement);
Var  win: TSimWindow;
Begin
     while (top <> nil) and not (top is TSimWindow_Element) do
        top := top.UpperElem;

     if top <> nil then begin

        CreateViewBranch (top);
        SetupViewBranch (top);

        if top.Product is TSimWindow then begin
           win := top.Product as TSimWindow;
           win.Show;
        end;
     end;
End;

END.

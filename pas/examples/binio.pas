UNIT BinIO;

{ Binary Input / Output }

INTERFACE

Uses SysUtils {type Exception},
     Classes  {type TStream};

// Type EIO = class (Exception);

{--------------------------------------------------------------------------}

Const BufSize = 1024;

Type TInput = class
     private
        InpStream: TStream;

     protected
        BufPos: integer;
        BufLen: integer;
        // Buf:    array [0..BufSize-1] of byte;

        procedure Init; virtual;
        procedure ReadBuf;
        procedure ReadData (adr: pointer; size: integer);

     public
        constructor Create (stream: TStream);
        procedure Error (const msg: string);
     end;

{--------------------------------------------------------------------------}

Type TOutput = class
     private
        OutStream: TStream;

     protected
        BufLen: integer;
        // Buf:    array [0..BufSize-1] of byte;

        procedure Init; virtual;

        procedure WriteBuf;
        procedure WriteData (adr: pointer; size: integer);

     public
        constructor Create (stream: TStream);
        procedure Flush;
        destructor Destroy; override;

        procedure Error (const msg: string);
     end;

{--------------------------------------------------------------------------}

Type TBinInput = class (TInput)
     private
        procedure ReadCode (var x: integer);

     public
        procedure CheckEof;

        function ReadBoolean: Boolean;
        function ReadEnum (size: integer): integer;
        function ReadChar: Char;
        function ReadWideChar: WideChar;

        function ReadShortInt: ShortInt;
        function ReadSmallInt: SmallInt;
        function ReadInteger: Integer;
        function ReadInt64: Int64;

        function ReadByte: Byte;
        function ReadWord: Word;
        function ReadLongWord: LongWord;

        function ReadSingle: Single;
        function ReadDouble: Double;
        function ReadExtended: Extended;

        function ReadString: String;
        {$IFNDEF FPC} function ReadWideString: WideString; {$ENDIF}
     end;

{--------------------------------------------------------------------------}

Type TBinOutput = class (TOutput)
     private
        procedure WriteCode (code: integer);

     public
        procedure WriteBoolean (value: Boolean);
        procedure WriteEnum (value, size: integer);
        procedure WriteChar (value: Char);
        procedure WriteWideChar (value: WideChar);

        procedure WriteShortInt (value: ShortInt);
        procedure WriteSmallInt (value: SmallInt);
        procedure WriteInteger (value: Integer);
        procedure WriteInt64 (value: Int64);

        procedure WriteByte (value: Byte);
        procedure WriteWord (value: Word);
        procedure WriteLongWord (value: LongWord);

        procedure WriteSingle (value: Single);
        procedure WriteDouble (value: Double);
        procedure WriteExtended (value: Extended);

        procedure WriteString (const s: String);
        {$IFNDEF FPC} procedure WriteWideString (const s: WideString); {$ENDIF}
     end;

{--------------------------------------------------------------------------}

{$IFNDEF CONV_NO_CLASSOF}
Procedure RegisterIO (AClass: TClass);
Function FindIO (const name: string): TClass;
{$ENDIF}

IMPLEMENTATION

{$IFNDEF FPC}
   Uses Consts; {const SClassNotFound}
{$ELSE}
   Const SClassNotFound = 'Class %s not found';
{$ENDIF}

(********************************* INPUT **********************************)

Constructor TInput.Create (stream: TStream);
Begin
     Assert (stream <> nil);
     InpStream := stream;

     BufPos := 0;
     BufLen := 0;

     Init;
End;

Procedure TInput.Error (const msg: string);
Begin
     raise EIO.Create (msg);
End;

Procedure TInput.Init;
Begin
     { nothing }
End;

{--------------------------------------------------------------------------}

Procedure TInput.ReadBuf;
Begin
     BufLen := InpStream.Read0 (Buf, BufSize);
     BufPos := 0;
End;

Procedure TInput.ReadData (adr: pointer; size: integer);
Var  step: integer;
Begin
     Assert (BufPos >= 0);
     Assert (BufPos <= BufLen);

     Assert (BufLen >= 0);
     Assert (BufLen <= BufSize);

     while size > 0 do begin
        if BufPos >= BufLen then begin
           ReadBuf;
           if BufLen = 0 then Error ('End of file');
        end;

        step := BufLen - BufPos;
        if step > size then step := size;

        Assert (step > 0);
        Assert (step <= size);

        Assert (BufPos >= 0);
        Assert (BufPos+step <= BufLen);

        Assert (BufLen >= 0);
        Assert (BufLen <= BufSize);

        move (Buf [BufPos], adr^, step);
        inc (BufPos, step);
        dec (size, step);

        {$IFDEF CONV}
           adr := Pointer (PChar (adr) + step);
        {$ELSE}
           inc (integer (adr), step);
        {$ENDIF}

        Assert (size >= 0);
     end;
End;

(********************************* OUTPUT *********************************)

Constructor TOutput.Create (stream: TStream);
Begin
     Assert (stream <> nil);
     OutStream := stream;
     BufLen := 0;
     Init;
End;

Destructor TOutput.Destroy;
Begin
     Flush;
     // innherited;
End;

Procedure TOutput.Error (const msg: string);
Begin
     raise EIO.Create (msg);
End;

Procedure TOutput.Init;
Begin
     { nothing }
End;

{--------------------------------------------------------------------------}

Procedure TOutput.WriteBuf;
Begin
     OutStream.WriteBuffer (Buf, BufLen);
     BufLen := 0;
End;

Procedure TOutput.WriteData (adr: pointer; size: integer);
Var  step: integer;
Begin
     while size > 0 do begin
        step := BufSize - BufLen;
        if step > size then step := size;

        Assert (step > 0);
        Assert (step <= size);

        Assert (BufLen >= 0);
        Assert (BufLen + step <= BufSize);

        move (adr^, Buf [BufLen], step);
        inc (BufLen, step);
        dec (size, step);

        {$IFDEF CONV}
           adr := Pointer (PChar (adr) + step);
        {$ELSE}
           inc (integer (adr), step);
        {$ENDIF}

        if BufLen = BufSize then WriteBuf;
     end;
End;

Procedure TOutput.Flush;
Begin
     if BufLen > 0 then WriteBuf;
End;

(****************************** BINARY INPUT ******************************)

Procedure TBinInput.CheckEof;
Var  eof: boolean;
Begin
     eof := (BufPos = BufLen);
     if eof then begin
        ReadBuf;
        eof := (BufLen = 0);
     end;
     if not eof then Error ('End of file expected');
End;

{--------------------------------------------------------------------------}

Function TBinInput.ReadBoolean: Boolean;
Begin
     ReadData (@result, sizeof (result));
End;

Function TBinInput.ReadEnum (size: integer): integer;
Begin
     result := 0; { clear high bits }
     ReadData (@result, size);
End;

Function TBinInput.ReadChar: Char;
Begin
     ReadData (@result, sizeof (result));
End;

Function TBinInput.ReadWideChar: WideChar;
Begin
     ReadData (@result, sizeof (result));
End;

{--------------------------------------------------------------------------}

Function TBinInput.ReadShortInt: ShortInt;
Begin
     ReadData (@result, sizeof (result));
End;

Function TBinInput.ReadSmallInt: SmallInt;
Begin
     ReadData (@result, sizeof (result));
End;

Function TBinInput.ReadInteger: Integer;
Begin
     ReadData (@result, sizeof (result));
End;

Function TBinInput.ReadInt64: Int64;
Begin
     ReadData (@result, sizeof (result));
End;

{--------------------------------------------------------------------------}

Function TBinInput.ReadByte: Byte;
Begin
     ReadData (@result, sizeof (result));
End;

Function TBinInput.ReadWord: Word;
Begin
     ReadData (@result, sizeof (result));
End;

Function TBinInput.ReadLongWord: LongWord;
Begin
     ReadData (@result, sizeof (result));
End;

{--------------------------------------------------------------------------}

Function TBinInput.ReadSingle: Single;
Begin
     ReadData (@result, sizeof (result));
End;

Function TBinInput.ReadDouble: Double;
Begin
     ReadData (@result, sizeof (result));
End;

Function TBinInput.ReadExtended: Extended;
Begin
     ReadData (@result, sizeof (result));
End;


{--------------------------------------------------------------------------}

Procedure TBinInput.ReadCode (var x: integer);
Var  n: byte;
Begin
     ReadData (@n, 1);
     if n < 255 then x := n
                else ReadData (@x, sizeof (x));
End;

Function TBinInput.ReadString: String;
Var  n: integer;
Begin
     ReadCode (n);
     SetString (result, nil, n);
     ReadData (PChar (result), n);
End;

{$IFNDEF FPC}
Function TBinInput.ReadWideString: WideString;
Var  n: integer;
Begin
     ReadCode (n);
     SetString (result, nil, n*2); {!}
     ReadData (PWideChar (result), n*2);
End;
{$ENDIF}

(***************************** BINARY OUTPUT ******************************)

Procedure TBinOutput.WriteBoolean (value: Boolean);
Begin
     WriteData (@value, sizeof (value));
End;

Procedure TBinOutput.WriteEnum (value: integer; size: integer);
Begin
     WriteData (@value, size);
End;

Procedure TBinOutput.WriteChar (value: Char);
Begin
     WriteData (@value, sizeof (value));
End;

Procedure TBinOutput.WriteWideChar (value: WideChar);
Begin
     WriteData (@value, sizeof (value));
End;

{--------------------------------------------------------------------------}

Procedure TBinOutput.WriteShortInt (value: ShortInt);
Begin
     WriteData (@value, sizeof (value));
End;

Procedure TBinOutput.WriteSmallInt (value: SmallInt);
Begin
     WriteData (@value, sizeof (value));
End;

Procedure TBinOutput.WriteInteger (value: Integer);
Begin
     WriteData (@value, sizeof (value));
End;

Procedure TBinOutput.WriteInt64 (value: Int64);
Begin
     WriteData (@value, sizeof (value));
End;

{--------------------------------------------------------------------------}

Procedure TBinOutput.WriteByte (value: Byte);
Begin
     WriteData (@value, sizeof (value));
End;

Procedure TBinOutput.WriteWord (value: Word);
Begin
     WriteData (@value, sizeof (value));
End;

Procedure TBinOutput.WriteLongWord (value: LongWord);
Begin
     WriteData (@value, sizeof (value));
End;

{--------------------------------------------------------------------------}

Procedure TBinOutput.WriteSingle (value: Single);
Begin
     WriteData (@value, sizeof (value));
End;

Procedure TBinOutput.WriteDouble (value: Double);
Begin
     WriteData (@value, sizeof (value));
End;

Procedure TBinOutput.WriteExtended (value: Extended);
Begin
     WriteData (@value, sizeof (value));
End;

{--------------------------------------------------------------------------}

Procedure TBinOutput.WriteCode (code: integer);
Var  n: byte;
Begin
     if (code >= 0) and (code <= 254) then
        WriteData (@code, 1)
     else begin
        n := 255;
        WriteData (@n, 1);
        WriteData (@code, sizeof (code));
     end;
End;

Procedure TBinOutput.WriteString (const s: String);
Var  n: integer;
Begin
     n := length (s);
     WriteCode (n);
     WriteData (PChar (s), n);
End;

{$IFNDEF FPC}
Procedure TBinOutput.WriteWideString (const s: WideString);

Var  n: integer;
Begin
     n := length (s);
     WriteCode (n);
     WriteData (PWideChar (s), n*2);
End;
{$ENDIF}

(****************************** REGISTRATION ******************************)

{$IFNDEF CONV_NO_CLASSOF}

Type TClassEntry = class
     public
        Prev: TClassEntry;
        Next: TClassEntry;
        cls:  TClass;
     end;

     TClassList = class
     public
        First: TClassEntry;
        Last:  TClassEntry;
        procedure Add (item: TClassEntry);
     end;

Var ClassList: TClassList;

Procedure TClassList.Add (item: TClassEntry);
Begin
     Assert (item <> nil);

     item.Prev := Last;
     item.Next := nil;

     if Last = nil then First := item
                   else Last.Next := item;
     Last := item;
End;

Procedure RegisterIO (AClass: TClass);
Var  p: TClassEntry;
Begin
     if ClassList = nil then
        ClassList := TClassList.Create;

     p := ClassList.First;
     while (p <> nil) and (p.cls <> AClass) do
        p := p.Next;

     if p = nil then begin
        p := TClassEntry.Create;
        p.cls := AClass;
        ClassList.Add (p);
     end;
End;

Function FindIO (const name: string): TClass;
Var  p: TClassEntry;
Begin
     if ClassList = nil then
        p := nil
     else begin
        p := ClassList.First;
        while (p <> nil) and (CompareText (p.cls.ClassName, name) <> 0) do
           p := p.Next;
     end;

     if p = nil then
        raise EClassNotFound.Create (Format (SClassNotFound, [name]));

     result := p.cls;
End;

{$ENDIF}

END.


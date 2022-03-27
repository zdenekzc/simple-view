UNIT TextIO;

{ Text Input / Output }

INTERFACE

Uses SysUtils, {type Exception}
     {$IFNDEF CONV_NO_TYPEINFO} TypInfo, {type PTypeInfo} {$ENDIF}
     BinIO;    {type TInput, TOutput}

{--------------------------------------------------------------------------}

Type TToken  = (IdentTok,
                NumberTok,
                StringTok,
                SeparatorTok,
                EofTok);

Const DuplMax = 255;

Type TTextInput = class (TInput)
     private
        LinePos: integer;
        ColPos:  integer;
        CharPos: integer;

        InpCh:   char;
        InpEof:  boolean;

        DuplLen: integer;
        DuplBuf: string [DuplMax];

        procedure GetCh;
        procedure NextCh;

        procedure Digits;

        procedure GetIdent;
        procedure GetNumber;
        procedure GetString;

        procedure OutOfRange;

     protected
        procedure Init; override;

     public
        TokenLine:    integer;
        TokenCol:     integer;
        TokenPos:     integer;

        Token:        TToken;
        IdentTxt:     string;
        NumberTxt:    string;
        StringTxt:    string;
        SeparatorTxt: char;

        procedure Error (const msg: string);

        procedure GetToken;

        function ReadNumber: string;
        function GetLine: string;

        procedure CheckIdent (const par: string);
        procedure CheckSeparator (par: char);
        procedure CheckEof;

        function IsIdent (const par: string): boolean;
        function IsSeparator (par: char): boolean;
        function IsEof: boolean;

        function ReadIdent: string;

        function ReadBoolean: Boolean;
        {$IFNDEF CONV_NO_TYPEINFO} function ReadEnum (info: PTypeInfo): integer; {$ENDIF}
        function ReadChar: Char;

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
     end;

{--------------------------------------------------------------------------}

Type TTextOutput = class (TOutput)
     private
        Indent: integer;
        Start:  boolean;

        procedure PutCh (c: char);
        procedure PutIndent;

     protected
        procedure Init; override;

     public
        LinePos: integer;
        ColPos:  integer;

        procedure Put (const s: string);
        procedure PutEol;
        procedure PutLn (const s: string);

        procedure SetIndent (i: integer);
        procedure IncIndent;
        procedure DecIndent;

        procedure WriteBoolean  (value: Boolean);
        {$IFNDEF CONV_NO_TYPEINFO} procedure WriteEnum (value: integer; info: PTypeInfo); {$ENDIF}
        procedure WriteChar     (value: Char);

        procedure WriteShortInt (value: ShortInt);
        procedure WriteSmallInt (value: SmallInt);
        procedure WriteInteger  (value: Integer);
        procedure WriteInt64    (value: Int64);

        procedure WriteByte     (value: Byte);
        procedure WriteWord     (value: Word);
        procedure WriteLongWord (value: Longword);

        procedure WriteSingle   (value: Single);
        procedure WriteDouble   (value: Double);
        procedure WriteExtended (value: Extended);

        procedure WriteString   (const value: String);
     end;

IMPLEMENTATION

(********************************* INPUT **********************************)

Const cr = ^M;
      lf = ^J;

Procedure TTextInput.Init;
Begin
     LinePos := 1;
     ColPos := 0;

     { not necessary }
     InpCh := chr (0);
     InpEof := false;
     DuplLen := 0;
     DuplBuf := '';
     Token := SeparatorTok;
     IdentTxt := '';
     NumberTxt := '';
     StringTxt := '';
     SeparatorTxt := chr (0);

     { read first character }
     GetCh;
End;

Procedure TTextInput.Error (const msg: string);
Begin
     inherited Error ('Line: ' + IntToStr (LinePos) + ' ' +
                      'Col: ' + IntToStr (ColPos) + ' ' + msg);
End;

Procedure TTextInput.GetCh;
Begin
     Assert (BufPos >= 0);
     Assert (BufPos <= BufLen);

     Assert (BufLen >= 0);
     Assert (BufLen <= BufSize);

     if BufPos >= BufLen then begin
        if InpEof then Error ('End of file');
        ReadBuf;
        InpEof := (BufLen = 0);
     end;

     if InpEof then
        InpCh := chr (0)
     else begin
        Assert (BufPos >= 0);
        Assert (BufPos < BufLen);

        Assert (BufLen >= 0);
        Assert (BufLen <= BufSize);

        InpCh := char (Buf [BufPos]);
        inc (BufPos);
     end;

     Assert (BufPos >= 0);
     Assert (BufPos <= BufLen);

     Assert (BufLen >= 0);
     Assert (BufLen <= BufSize);

     if InpCh = lf then begin
        inc (LinePos);
        ColPos := 0;
     end
     else inc (ColPos);

     inc (CharPos);

     // write (InpCh); { !! debug }
End;

{--------------------------------------------------------------------------}

Procedure TTextInput.NextCh;
Begin
     if DuplLen >= DuplMax then Error ('Token too long');
     inc (DuplLen);
     DuplBuf [DuplLen] := InpCh;

     GetCh;
End;

{--------------------------------------------------------------------------}

Const letter = ['A'..'Z', 'a'..'z', '_'];
      digit  = ['0'..'9'];
      lod    = letter + digit;

      quote  = '''';

Procedure TTextInput.GetIdent;
Begin
     DuplLen := 0;
     while InpCh in lod do NextCh;

     { set length }
     SetLength (DuplBuf, DuplLen);
     IdentTxt := DuplBuf;

     Token := IdentTok;
End;

Procedure TTextInput.Digits;  { digit <digit> }
Begin
     if not (InpCh in digit) then Error ('Digit expected');
     while InpCh in digit do NextCh;
End;

Procedure TTextInput.GetNumber;
Begin
     DuplLen := 0;
     Digits;                                     { digit <digit> }

     if InpCh='.' then begin                     { '.' digit <digit> }
        NextCh;
        Digits;
     end;

     if (InpCh='E') or (InpCh='e') then begin
        NextCh;
        if (InpCh='+') or (InpCh='-') then NextCh;
        Digits;
     end;

     { set length }
     SetLength (DuplBuf, DuplLen);
     NumberTxt := DuplBuf;

     Token := NumberTok;
End;

Procedure TTextInput.GetString;

Const TxtMax = 255;
Var   len: integer;
      txt: string [TxtMax];
      n: integer;
Begin
     DuplLen := 0;
     len := 0;

     while InpCh in [quote, '#', '^'] do begin

        if InpCh = quote then begin
           repeat
              repeat
                 NextCh;
                 if (InpCh = cr) or (InpCh = lf) then
                    Error ('String exceeds line');

                 inc (len);
                 if len > TxtMax then Error ('String too long');
                 txt [len] := InpCh;
              until InpCh = quote;
              NextCh;
           until InpCh <> quote;
           dec (len);
        end

        else if InpCh = '#' then begin
           NextCh; { skip # }
           if not (InpCh in digit) then Error ('Digit expected');
           n := 0;
           while InpCh in digit do begin
              n := n*10 + ord (InpCh) - ord ('0');
              if n > 255 then Error ('Bad character code');
              NextCh;
           end;

           inc (len);
           if len > TxtMax then Error ('String too long');
           txt [len] := chr (n);
        end

        else begin
           NextCh; { skip ^ }
           n := ord (InpCh) - 64;
           if (n < 0) or (n > 31) then Error ('Bad control character');
           NextCh; { skip character }

           inc (len);
           if len > TxtMax then Error ('String too long');
           txt [len] := chr (n);
        end;

     end; {while}

     { set length }
     SetLength (DuplBuf, DuplLen);
     SetLength (txt, len);
     StringTxt := txt;

     Token := StringTok;
End;

Procedure TTextInput.GetToken;

Begin
     while (InpCh <= ' ') and not InpEof do GetCh;         { WHITE SPACE }

     TokenLine := LinePos;
     TokenCol  := ColPos;
     TokenPos  := CharPos;

     if InpCh in letter then GetIdent                      { IDENTIFIER }
     else if InpCh in digit then GetNumber                 { NUMBER }
     else if InpCh in [quote, '#'] then GetString          { STRING }

     else if not InpEof then begin                         { SEPARATOR }
        Token := SeparatorTok;
        SeparatorTxt := InpCh;
        DuplBuf := InpCh;
        GetCh;
     end

     else begin                                            { END OF FILE }
        Token := EofTok;
        DuplBuf := '';
     end;
End;

{--------------------------------------------------------------------------}

Function TTextInput.GetLine: string;
Begin
     TokenLine := LinePos;
     TokenCol  := ColPos;
     TokenPos  := CharPos;

     { read rest of line }
     DuplLen := 0;
     while not InpEof and (InpCh <> cr) and (InpCh <> lf) do NextCh;

     { skip end of line }
     if not InpEof and (InpCh = cr) then GetCh;
     if not InpEof and (InpCh = lf) then GetCh;


     { set length }
     SetLength (DuplBuf, DuplLen);
     IdentTxt := DuplBuf;

     { string token !? }
     Token := StringTok;
     StringTxt := DuplBuf;

     result := DuplBuf;
End;

{--------------------------------------------------------------------------}

Procedure TTextInput.CheckIdent (const par: string);
Begin
     if (Token <> IdentTok) or (CompareText (IdentTxt, par) <> 0) then
        Error (par + ' expected');
     GetToken;
End;

Procedure TTextInput.CheckSeparator (par: char);
Begin
     if (Token <> SeparatorTok) or (SeparatorTxt <> par) then
        Error (par + ' expected');
     GetToken;
End;

Procedure TTextInput.CheckEof;
Begin
     if Token <> EofTok then
        Error ('End of file expected');
End;

{--------------------------------------------------------------------------}

Function TTextInput.IsIdent (const par: string): boolean;
Begin
     result := (Token = IdentTok) and (CompareText (IdentTxt, par) = 0);
End;

Function TTextInput.IsSeparator (par: char): boolean;
Begin
     result := (Token = SeparatorTok) and (SeparatorTxt = par);
End;

Function TTextInput.IsEof: boolean;
Begin
     result := (Token = EofTok);
End;

{--------------------------------------------------------------------------}

Function TTextInput.ReadIdent: string;
Begin
     if Token <> IdentTok then Error ('Identifier expected: ' + DuplBuf);
     result := IdentTxt;
     GetToken;
End;

Function TTextInput.ReadNumber: string;
Var  minus: boolean;
Begin
     minus := false;
     if (Token = SeparatorTok) and (SeparatorTxt = '-') then begin
        minus := true;
        GetToken;
     end;

     if Token <> NumberTok then Error ('Number expected');
     result := NumberTxt;
     if minus then result := '-' + result;
     GetToken;
End;

Function TTextInput.ReadString: string;
Begin
     if Token <> StringTok then Error ('String expected');
     result := StringTxt;
     GetToken;
End;

Procedure TTextInput.OutOfRange;
Begin
     Error ('Value out of range');
End;

(*************************** INPUT - ATTRIBUTES ***************************)

Function TTextInput.ReadBoolean: Boolean;
Begin
     if IsIdent ('TRUE') then begin
        result := true;
        GetToken;
     end
     else if IsIdent ('FALSE') then begin
        result := false;
        GetToken;
     end
     else begin
        result := false; { compiler }
        Error ('Boolean value expected');
     end;
End;

{$IFNDEF CONV_NO_TYPEINFO}
Function TTextInput.ReadEnum (info: PTypeInfo): integer;
Begin
     if Token <> IdentTok then Error ('Identifier expected');
     result := GetEnumValue (info, IdentTxt);
     if result = -1 then Error ('Unknown identifier');
     GetToken;
End;
{$ENDIF}

Function TTextInput.ReadChar: Char;
Begin
     if (Token <> StringTok) or (length (StringTxt) <> 1) then
        Error ('Character constant expected');
     result := StringTxt [1];
     GetToken;
End;

{--------------------------------------------------------------------------}

Function TTextInput.ReadShortInt: ShortInt;
Var  code: integer;
Begin
     val (ReadNumber, result, code);
     if code <> 0 then OutOfRange;
End;

Function TTextInput.ReadSmallInt: SmallInt;
Var  code: integer;
Begin
     val (ReadNumber, result, code);
     if code <> 0 then OutOfRange;
End;

Function TTextInput.ReadInteger: Integer;
Var  code: integer;
Begin
     val (ReadNumber, result, code);
     if code <> 0 then OutOfRange;
End;

Function TTextInput.ReadInt64: Int64;
Var  code: integer;
Begin
     val (ReadNumber, result, code);
     if code <> 0 then OutOfRange;
End;

{--------------------------------------------------------------------------}

Function TTextInput.ReadByte: Byte;
Var  code: integer;
Begin
     val (ReadNumber, result, code);
     if code <> 0 then OutOfRange;
End;

Function TTextInput.ReadWord: Word;
Var  code: integer;
Begin
     val (ReadNumber, result, code);
     if code <> 0 then OutOfRange;
End;

Function TTextInput.ReadLongWord: LongWord;
Var  code: integer;
Begin
     val (ReadNumber, result, code);
     if code <> 0 then OutOfRange;
End;

{--------------------------------------------------------------------------}

Function TTextInput.ReadSingle: Single;
Var  code: integer;
Begin
     val (ReadNumber, result, code);
     if code <> 0 then OutOfRange;
End;

Function TTextInput.ReadDouble: Double;
Var  code: integer;
Begin
     val (ReadNumber, result, code);
     if code <> 0 then OutOfRange;
End;

Function TTextInput.ReadExtended: Extended;
Var  code: integer;
Begin
     val (ReadNumber, result, code);
     if code <> 0 then OutOfRange;
End;


(********************************* OUTPUT *********************************)

Procedure TTextOutput.Init;
Begin
     Indent := 0;
     Start := true;

     LinePos := 1;
     ColPos := 0;
End;

Procedure TTextOutput.SetIndent (i: integer);
Begin
     Indent := i;
End;

Procedure TTextOutput.IncIndent;
Begin
     inc (Indent, 3);
End;

Procedure TTextOutput.DecIndent;
Begin
     dec (Indent, 3);
End;

Procedure TTextOutput.PutCh (c: char);
Begin
     Assert (BufLen >= 0);
     Assert (BufLen <= BufSize);

     if BufLen >= BufSize then WriteBuf;
     Assert (BufLen < BufSize);

     Buf [BufLen] := ord (c);
     inc (BufLen);

     if c = lf then begin
        inc (LinePos);
        ColPos := 0;
     end
     else inc (ColPos);

     Assert (BufLen >= 0);
     Assert (BufLen <= BufSize);
End;

Procedure TTextOutput.PutIndent;
Var  i: integer;
Begin
     if Start then begin
        for i := 1 to indent do PutCh (' ');
        Start := false;
     end;
End;

Procedure TTextOutput.Put (const s: string);
Var  i: integer;
Begin
     if Start then PutIndent;

     for i := 1 to length (s) do
        PutCh (s[i]);
End;

Procedure TTextOutput.PutEol;
Begin
     PutCh (cr);
     PutCh (lf);
     Start := true;
End;

Procedure TTextOutput.PutLn (const s: string);
Begin
     Put (s);
     PutEol;
End;

(************************** OUTPUT - ATTRIBUTES ***************************)

Procedure TTextOutput.WriteBoolean (value: Boolean);
Begin
     if value then Put ('true') else Put ('false');
End;

{$IFNDEF CONV_NO_TYPEINFO}
Procedure TTextOutput.WriteEnum (value: integer; info: PTypeInfo);
Begin
     Put (GetEnumName (info, value));
End;
{$ENDIF}

Procedure TTextOutput.WriteChar (value: Char);
Begin
     WriteString (value);
End;

{--------------------------------------------------------------------------}

Procedure TTextOutput.WriteShortInt (value: ShortInt);
Begin
     Put (IntToStr (value));
End;

Procedure TTextOutput.WriteSmallInt (value: SmallInt);
Begin
     Put (IntToStr (value));
End;

Procedure TTextOutput.WriteInteger (value: Integer);
Begin
     Put (IntToStr (value));
End;

Procedure TTextOutput.WriteInt64 (value: Int64);
Begin
     Put (IntToStr (value));
End;

{--------------------------------------------------------------------------}

Procedure TTextOutput.WriteByte (value: Byte);
Begin
     Put (IntToStr (value));
End;

Procedure TTextOutput.WriteWord (value: Word);
Begin
     Put (IntToStr (value));
End;

Procedure TTextOutput.WriteLongWord (value: LongWord);
Begin
     Put (IntToStr (value));
End;

{--------------------------------------------------------------------------}

Procedure TTextOutput.WriteSingle (value: Single);
Var  txt: string;
Begin
     str (value, txt);
     Put (txt);
End;

Procedure TTextOutput.WriteDouble (value: Double);
Var  txt: string;
Begin
     str (value, txt);
     Put (txt);
End;

Procedure TTextOutput.WriteExtended (value: Extended);
Var  txt: string;
Begin
     str (value, txt);
     Put (txt);
End;

{--------------------------------------------------------------------------}

Procedure TTextOutput.WriteString (const value: String);
Var  i:   integer;
     c:   char;
     seq: boolean;
Begin
     if Start then PutIndent;

     if value = '' then begin
        PutCh (quote);
        PutCh (quote);
     end
     else begin
        seq := false;

        for i := 1 to length (value) do begin
           c := value[i];

           if c < ' ' then begin
              if seq then begin
                 PutCh (quote);
                 seq := false;
              end;
              PutCh ('#');
              Put (IntToStr (ord (c)));
           end
           else begin
              if not seq then begin
                 PutCh (quote);
                 seq := true;
              end;
              PutCh (c);
              if c = quote then PutCh (quote);
           end;
        end;

        if seq then PutCh (quote);
     end;
End;

END.


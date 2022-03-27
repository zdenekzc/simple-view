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

        procedure Init; // virtual;
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

        procedure Init; // virtual;

        procedure WriteBuf;
        procedure WriteData (adr: pointer; size: integer);

     public
        constructor Create (stream: TStream);
        procedure Flush;
        destructor Destroy; // override;

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
     end;

{--------------------------------------------------------------------------}

Procedure RegisterIO (AClass: TClass);
Function FindIO (const name: string): TClass;

IMPLEMENTATION

END.


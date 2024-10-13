















import sys
import traceback




class Lexer :

  def __init__ (self) :
    pass



  def yylex (self) :
    return (0,None)


  def yyerror (self, msg) :
    s = msg
    
    sys.stderr.write(s+'\n')




YYACCEPT = 0

YYABORT = 1
YYERROR = 2




YYERRLAB = 3
YYNEWSTATE = 4
YYDEFAULT = 5
YYREDUCE = 6
YYERRLAB1 = 7
YYRETURN = 8



YYACTION = 10

LABELNAMES = (
"YYACCEPT",
"YYABORT",
"YYERROR",
"YYERRLAB",
"YYNEWSTATE",
"YYDEFAULT",
"YYREDUCE",
"YYERRLAB1",
"YYRETURN",
"YYGETTOKEN",
"YYACTION"
)


EOF = 0


YYEOF = 0
YYerror = 256
YYUNDEF = 257
INT_LITERAL = 258
NAME = 259
NEGATE = 260
INDENT = 261
DEDENT = 262
EOL = 263








def yy_pact_value_is_default_ (yyvalue) :
  return yyvalue == yypact_ninf_


def yy_table_value_is_error_ (yyvalue) :
  return yyvalue == yytable_ninf_


yypact_ = (
      36,   -45,    49,    41,    41,    41,     4,   -45,   -45,    63,
      41,     1,    31,    41,    -2,    17,    63,    18,    15,   -45,
      19,   -45,    36,    41,    41,    41,    41,    41,    63,    41,
      38,    28,    30,    41,   -45,    41,   -45,   -45,     6,     6,
      17,    17,    17,    63,    36,    46,   -45,    37,   -45,    43,
      36,   -45,    36,    48,    13,    36,   -45,    45,   -45
  )

yydefact_ = (
       0,    14,    15,     0,     0,     0,     0,     2,     4,     5,
       0,     0,     0,     0,    15,    22,    30,     0,    26,    28,
       0,     1,     0,     0,     0,     0,     0,     0,     6,     0,
       0,     0,     0,     0,    24,    27,    25,     3,    19,    18,
      20,    21,    23,     7,     8,    16,    17,     0,    29,     9,
      11,    16,     0,    12,     0,     0,    10,     0,    13
  )

yypgoto_ = (
     -45,   -44,   -19,   -45,    -3,     0,   -45,    29
  )

yydefgoto_ = (
       0,     6,     7,     8,     9,    17,    18,    19
  )

yytable_ = (
      15,    16,    16,    37,    21,    20,    29,    28,    54,    16,
      16,    57,    31,    32,    25,    33,    26,    13,    27,    22,
      38,    39,    40,    41,    42,    49,    43,    56,    22,    27,
      16,    53,    16,    47,     1,    14,    34,     3,    35,     1,
       2,    36,     3,    44,     1,    14,    45,     3,     4,    30,
      46,    50,     5,     4,    10,    51,    52,     5,     4,    58,
      22,    55,     5,     0,    48,    11,    12,     0,    13,    23,
      24,    25,     0,    26,     0,    27
  )

yycheck_ = (
       3,     4,     5,    22,     0,     5,     5,    10,    52,    12,
      13,    55,    12,    13,     8,    17,    10,    19,    12,    15,
      23,    24,    25,    26,    27,    44,    29,    14,    15,    12,
      33,    50,    35,    33,     3,     4,    18,     6,    23,     3,
       4,    22,     6,     5,     3,     4,    18,     6,    17,    18,
      20,     5,    21,    17,     5,    18,    13,    21,    17,    14,
      15,    13,    21,    -1,    35,    16,    17,    -1,    19,     6,
       7,     8,    -1,    10,    -1,    12
  )

yystos_ = (
       0,     3,     4,     6,    17,    21,    25,    26,    27,    28,
       5,    16,    17,    19,     4,    28,    28,    29,    30,    31,
      29,     0,    15,     6,     7,     8,    10,    12,    28,     5,
      18,    29,    29,    17,    18,    23,    22,    26,    28,    28,
      28,    28,    28,    28,     5,    18,    20,    29,    31,    26,
       5,    18,    13,    26,    25,    13,    14,    25,    14
  )

yyr1_ = (
       0,    24,    25,    25,    26,    26,    27,    27,    27,    27,
      27,    27,    27,    27,    28,    28,    28,    28,    28,    28,
      28,    28,    28,    28,    28,    28,    29,    29,    30,    30,
      31
  )

yyr2_ = (
       0,     2,     1,     3,     1,     1,     3,     4,     4,     5,
       8,     5,     6,     9,     1,     1,     4,     4,     3,     3,
       3,     3,     2,     3,     3,     3,     1,     2,     1,     3,
       1
  )


yytoken_number_ = (
       0,   256,   257,   258,   259,    61,    45,    43,    42,    64,
      47,   260,    94,   261,   262,   263,    95,    40,    41,    91,
      93,   123,   125,    44
  )

yytname_ = (
  "\"end of file\"", "error", "\"invalid token\"", "INT_LITERAL", "NAME",
  "'='", "'-'", "'+'", "'*'", "'@'", "'/'", "NEGATE", "'^'", "INDENT",
  "DEDENT", "EOL", "'_'", "'('", "')'", "'['", "']'", "'{'", "'}'", "','",
  "$accept", "stmts", "stmt", "define", "expr", "named_exprs",
  "named_expr_i", "named_expr", None
  )

yyrline_ = (
       0,    29,    29,    30,    34,    35,    39,    40,    41,    42,
      43,    44,    45,    46,    50,    51,    52,    53,    54,    55,
      56,    57,    58,    59,    60,    61,    65,    66,    70,    71,
      75
  )

yytranslate_table_ = (
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
      17,    18,     8,     7,    23,     6,     2,    10,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     5,     2,     2,     9,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,    19,     2,    20,    12,    16,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,    21,     2,    22,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     2,     3,     4,
      11,    13,    14,    15
  )

def yytranslate_ (t) :
  if (t >= 0 and t <= yyuser_token_number_max_) :
    return yytranslate_table_[t]
  else :
    return yyundef_token_


yylast_ = 75
yynnts_ = 8
yyempty_ = -2
yyfinal_ = 21
yyterror_ = 1
yyerrcode_ = 256
yyntokens_ = 24

yyuser_token_number_max_ = len(yytranslate_table_)-1 #e4_user_token_number_max
yyundef_token_ = 2 #e4_undef_token_number

yypact_ninf_ = -45
yytable_ninf_ = -1




class YYStack :

  def __init__ (self) :
    self.size = 16
    self.height = -1
    self.stateStack=[]
    self.valueStack=[]
    

  def push (self, state, value, ) :
    self.height += 1
    self.stateStack.append(state)
    self.valueStack.append(value)
    

  def pop (self, num) :
    if (num > 0) :
      for i in range(num) :
        self.valueStack.pop()
        self.stateStack.pop()
        
    self.height -= num

  def stateAt (self, i) :
    return self.stateStack[self.height - i]

  
  def valueAt (self, i) :
    return self.valueStack[self.height - i]

  def yyprint (self, out) :
    out.write ("Stack now")
    for x in self.stateStack[:] :
        out.write (' ')
        out.write (str(x))
    out.write ('\n')




class YYVAL:
  def __init__(self,yyval): self.yyval = yyval


class YYParser :
  bisonVersion = "30802"

  bisonSkeleton = "src/alang/langs/py.skel"





  def getErrorVerbose(self) :
    return self.yyErrorVerbose

  def setErrorVerbose(self, verbose) :
    self.yyErrorVerbose = verbose


  def getDebugStream (self) :
    return self.yyDebugStream

  def setDebugStream(self, s) :
    self.yyDebugStream = s

  def getDebugLevel (self) :
    return self.yydebug

  def setDebugLevel (self, level) :
    self.yydebug = level



  def __init__  (self, yylexer):

    self.yylexer = yylexer


    self.yyDebugStream = sys.stderr
    self.yydebug = 0
    self.yyerrstatus_ = 0


    self.yyErrorVerbose = True
    self.yyswitch_init()




  def yyswitch_init(self):
    self.yyswitch = {}








  def yyaction (self, yyn, yystack, yylen, yyerror) :
    yylval = None
    

    if (yylen > 0) :
      yyval = yystack.valueAt (yylen - 1)
    else :
      yyval = yystack.valueAt (0)

    self.yy_reduce_print (yyn, yystack)


    if (yyn in self.yyswitch) :
      action = self.yyswitch[yyn]
      yyvalp = YYVAL(yyval)
      status = action(yyvalp, yyn, yystack, yylen, yyerror)
      yyval = yyvalp.yyval
      if(status != None) : return status
    else: # no such action index; ignore
      pass

    self.yy_symbol_print ("-> $$ =",
                          yyr1_[yyn], yyval)

    yystack.pop (yylen)
    yylen = 0

    yyn = yyr1_[yyn]
    tmp = yyntokens_ # quote problem
    yystate = yypgoto_[yyn - tmp] + yystack.stateAt (0)
    if (0 <= yystate
        and yystate <= yylast_
        and yycheck_[yystate] == yystack.stateAt (0)) :
      yystate = yytable_[yystate]
    else :
      yystate = yydefgoto_[yyn - tmp]

    yystack.push (yystate, yyval)
    return YYNEWSTATE


  def yy_reduce_print (self, yyrule, yystack) :
    if (self.yydebug == 0) :
      return

    yylno = yyrline_[yyrule]
    yynrhs = yyr2_[yyrule]
    self.yycdebug ("Reducing stack by rule " + str(yyrule - 1)
               + " (line " + str(yylno) + "), ")

    for yyi in range(yynrhs) :
      self.yy_symbol_print ("   $" + str(yyi + 1) + " =",
                       yystos_[yystack.stateAt(yynrhs - (yyi + 1))],
                       (yystack.valueAt (yynrhs-(yyi + 1))))





  def  parse (self) :
    

    yychar = yyempty_
    yytoken = 0

    yyn = 0
    yylen = 0
    yystate = 0
    yystack = YYStack ()
    label = YYNEWSTATE

    yynerrs_ = 0
    
    yylval = None





    self.yycdebug ("Starting parse\n")
    self.yyerrstatus_ = 0
    yystack.push (yystate,
                           yylval )





    while True :

      if label == YYNEWSTATE : # case YYNEWSTATE
        self.yycdebug ("Entering state " + str(yystate) + '\n')
        if (self.yydebug > 0) :
          yystack.yyprint (self.yyDebugStream)

        if (yystate == yyfinal_) :
          return True

        tmp = yystate
        yyn = yypact_[tmp]
        if (yy_pact_value_is_default_ (yyn)) :
            label = YYDEFAULT
            continue; # break switch


        if (yychar == yyempty_) :
          self.yycdebug ("Reading a token: ")
          yychar, yylval = self.yylexer.yylex()
          

        if (yychar <= EOF) :
          yychar = EOF
          yytoken = EOF
          self.yycdebug ("Now at end of input.\n")
        else :
          yytoken = yytranslate_ (yychar)
          self.yy_symbol_print ("Next token is",
                                yytoken,
                                yylval
                                
                                )

        yyn += yytoken
        tmp = yyn # Quote problem
        if (yyn < 0 
            or yylast_ < yyn
            or yycheck_[tmp] != yytoken) :
          label = YYDEFAULT

        elif (yytable_[tmp] <= 0) :
          yyn = yytable_[tmp]
          if (yy_table_value_is_error_ (yyn)) :
            label = YYERRLAB
          else :
            yyn = -yyn
            label = YYREDUCE
        else :
          tmp = yyn # Quote problem
          yyn = yytable_[tmp]
          self.yy_symbol_print ("Shifting",
                                yytoken,
                                yylval)

          yychar = yyempty_

          if (self.yyerrstatus_ > 0) :
              self.yyerrstatus_ -= 1

          yystate = yyn
          yystack.push (yystate,             yylval)
          label = YYNEWSTATE

      elif label == YYDEFAULT : #case YYDEFAULT
        tmp = yystate # Quote problem
        yyn = yydefact_[tmp]
        if (yyn == 0) :
          label = YYERRLAB
        else :
          label = YYREDUCE

      elif label == YYREDUCE : #case YYREDUCE
        tmp = yyn # Quote problem
        yylen = yyr2_[tmp]
        label = self.yyaction (yyn,         yystack, yylen, self.yylexer.yyerror)
        yystate = yystack.stateAt (0)

      elif label == YYERRLAB: #case YYERRLAB
        if (self.yyerrstatus_ == 0) :
          yynerrs_ += 1
          if (yychar == yyempty_) :
            yytoken = yyempty_
          tmp = self.yysyntax_error (yystate, yytoken)
          self.yyerror (tmp)

        
        if (self.yyerrstatus_ == 3) :

          if (yychar <= EOF) :
            if (yychar == EOF) :
              return False
          else :
            yychar = yyempty_

        label = YYERRLAB1

      elif label == YYERROR : #case YYERROR
        
        yystack.pop (yylen)
        yylen = 0
        yystate = yystack.stateAt (0)
        label = YYERRLAB1

      elif label == YYERRLAB1 : #case YYERRLAB1
        self.yyerrstatus_ = 3 # Each real token shifted decrements this.
        while True :
          tmp = yystate # Quote problem
          yyn = yypact_[tmp]
          if ( not yy_pact_value_is_default_ (yyn)) :
            yyn += yyterror_
            tmp = yyn # Quote problem
            if (0 <= yyn and yyn <= yylast_ \
                and yycheck_[tmp] == yyterror_) :
              yyn = yytable_[tmp]
              if (0 < yyn) :
                break # leave while loop

          if (yystack.height == 0) :
            return False

          
          yystack.pop (1)
          yystate = yystack.stateAt (0)
          if (self.yydebug > 0) :
            yystack.yyprint (self.yyDebugStream)

        if (label == YYABORT) :
          continue # Leave the switch.


        tmp = yyn
        self.yy_symbol_print ("Shifting", yystos_[tmp],
                         yylval)

        yystate = yyn
        yystack.push (yyn, yylval               )
        label = YYNEWSTATE
        continue # leave the switch

      elif label == YYACCEPT : # case YYACCEPT
        return True

      elif label == YYABORT: # case YYABORT
        return False

      else :
        assert False, "Unknown State:" + str(label)










  def yyerror (self, msg) :
    self.yylexer.yyerror (msg)

  def yycdebug (self, s) :
    if (self.yydebug > 0) :
      self.yyDebugStream.write (s+'\n')


  def yytnamerr_ (self, yystr) :
    yyr = ""
    if (yystr[0] == '"')  :
      l = len(yystr)
      i = 1
      while (True) :
        if (i >= l) : break
        c = yystr[i]
        if(c == "'" or c == ',') :
          continue
        if( c == '"'):
          return yyr
        if(c == '\\') :
          i += 1
          c = yystr[i]
          if(c != '\\') :
            break
        yyr = yyr + c
        i += 1
    elif (yystr ==  "$end") :
      return "end of input"
    return yystr;



  def yy_symbol_print (self, s, yytype, yyvaluep ) :
    if (self.yydebug > 0) :
      tag = " nterm "
      if (yytype < yyntokens_) :
        tag = " token "
      if (yyvaluep is None) :
        vps = "None"
      else :
        vps = str(yyvaluep)
      tname = yytname_[yytype]
      line = s + tag + tname
      line += " ("
      
      line += vps
      line += ')'
      self.yycdebug (line)

  def yysyntax_error (self, yystate, tok) :
  
    if (self.yyErrorVerbose) :

      if (tok  != yyempty_) :
        res = "syntax error, unexpected "
        res += (self.yytnamerr_ (yytname_[tok]))
        tmp = yystate
        yyn = yypact_[tmp]
        if ( not yy_pact_value_is_default_ (yyn)) :
          yyxbegin = 0
          if (yyn < 0) :
            yyxbegin =  - yyn
          yychecklim = yylast_ - yyn + 1
          yyxend = yychecklim
          if (yychecklim >= yyntokens_) :
            yyxend = yyntokens_
          count = 0
          for x in range(yyxbegin,yyxend) :
            tmp = yyn
            if (yycheck_[x + tmp] == x and x != yyterror_
                and  not yy_table_value_is_error_ (yytable_[x + tmp])) :
              count += 1
          if (count < 5) :
            count = 0
            for x in range(yyxbegin,yyxend) :
              tmp = yyn
              if (yycheck_[x + tmp] == x and x != yyterror_
                  and  not yy_table_value_is_error_ (yytable_[x + tmp])) :
                if (count == 0) :
                  res += ", expecting "
                else :
                  res += " or "
                count += 1
                res += (self.yytnamerr_ (yytname_[x]))
        return str(res)

    return "syntax error"

  



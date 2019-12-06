from sqlalchemy import \
    Column, \
    Integer as I, \
    Float as F, \
    String as S, \
    LargeBinary

Integer = Column(I)
Float = Column(F)
String = Column(S)
Blob = Column(LargeBinary)

from sqlalchemy import \
    Column, \
    Integer as I, \
    Float as F, \
    String as S, \
    LargeBinary

Integer = lambda *args, **kwargs: Column(I, *args, **kwargs)
Float = lambda *args, **kwargs: Column(F, *args, **kwargs)
String = lambda *args, **kwargs: Column(S, *args, **kwargs)
Blob = lambda *args, **kwargs: Column(LargeBinary, *args, **kwargs)


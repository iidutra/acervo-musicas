# Tom choices - all valid musical keys
TOM_CHOICES = [
    ('C', 'C (Dó Maior)'),
    ('Cm', 'Cm (Dó Menor)'),
    ('C#', 'C# (Dó# Maior)'),
    ('C#m', 'C#m (Dó# Menor)'),
    ('D', 'D (Ré Maior)'),
    ('Dm', 'Dm (Ré Menor)'),
    ('D#', 'D# (Ré# Maior)'),
    ('D#m', 'D#m (Ré# Menor)'),
    ('Eb', 'Eb (Mib Maior)'),
    ('E', 'E (Mi Maior)'),
    ('Em', 'Em (Mi Menor)'),
    ('F', 'F (Fá Maior)'),
    ('Fm', 'Fm (Fá Menor)'),
    ('F#', 'F# (Fá# Maior)'),
    ('F#m', 'F#m (Fá# Menor)'),
    ('G', 'G (Sol Maior)'),
    ('Gm', 'Gm (Sol Menor)'),
    ('G#', 'G# (Sol# Maior)'),
    ('G#m', 'G#m (Sol# Menor)'),
    ('Ab', 'Ab (Láb Maior)'),
    ('A', 'A (Lá Maior)'),
    ('Am', 'Am (Lá Menor)'),
    ('Bb', 'Bb (Sib Maior)'),
    ('Bbm', 'Bbm (Sib Menor)'),
    ('B', 'B (Si Maior)'),
    ('Bm', 'Bm (Si Menor)'),
    ('NI', 'Não Informado'),
]

# Audio type choices
TIPO_AUDIO_CHOICES = [
    ('ensaio', 'Ensaio'),
    ('voz_violao', 'Voz e Violão'),
    ('coral', 'Coral'),
    ('instrumental', 'Instrumental'),
    ('playback', 'Playback'),
    ('referencia', 'Referência Interna'),
]

# Link provider choices
PROVIDER_CHOICES = [
    ('youtube', 'YouTube'),
    ('spotify', 'Spotify'),
    ('apple_music', 'Apple Music'),
    ('site_externo', 'Site Externo'),
    ('generico', 'Link Genérico'),
]

# Link content type choices
TIPO_CONTEUDO_LINK_CHOICES = [
    ('video', 'Vídeo'),
    ('audio', 'Áudio'),
    ('cifra', 'Cifra'),
    ('letra', 'Letra'),
    ('referencia', 'Referência'),
]

# Cifra type choices
TIPO_CIFRA_CHOICES = [
    ('texto', 'Texto Digitado'),
    ('pdf', 'PDF'),
    ('link', 'Link Externo'),
]

# Celebration type choices
TIPO_CELEBRACAO_CHOICES = [
    ('missa_dominical', 'Missa Dominical'),
    ('missa_semanal', 'Missa Semanal'),
    ('missa_solenidade', 'Missa de Solenidade'),
    ('adoracao', 'Adoração'),
    ('retiro', 'Retiro'),
    ('encontro', 'Encontro'),
    ('outro', 'Outro'),
]

# Import type choices
TIPO_IMPORTACAO_CHOICES = [
    ('csv', 'CSV'),
    ('excel', 'Excel'),
    ('json', 'JSON'),
    ('zip', 'ZIP'),
]

# Import status choices
STATUS_IMPORTACAO_CHOICES = [
    ('pendente', 'Pendente'),
    ('processando', 'Processando'),
    ('concluido', 'Concluído'),
    ('erro', 'Erro'),
]

# Origin choices
ORIGEM_CHOICES = [
    ('manual', 'Cadastro Manual'),
    ('importacao', 'Importação'),
    ('migracao', 'Migração'),
]

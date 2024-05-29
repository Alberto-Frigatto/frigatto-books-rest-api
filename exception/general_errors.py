errors = {
    'DatabaseConnection': {
        'message': 'Erro de conexão no banco de dados',
        'status': 500,
    },
    'MethodNotAllowed': {
        'message': 'Método HTTP não permitido',
        'status': 405,
    },
    'InvalidContentType': {
        'message': 'Cabeçalho Content-Type inválido.',
        'status': 415,
    },
    'NoDataSent': {
        'message': 'Não foi enviado nenhum dado',
        'status': 400,
    },
    'InvalidDataSent': {
        'message': 'Os dados enviados são inválidos',
        'status': 400,
    },
    'InvalidJWT': {
        'message': 'Token JWT inválido',
        'status': 401,
    },
    'MissingJWT': {
        'message': 'O token JWT não foi enviado',
        'status': 401,
    },
    'MissingCSFR': {
        'message': 'O token CSFR não foi enviado',
        'status': 400,
    },
    'InvalidCSFR': {
        'message': 'Token CSFR inválido',
        'status': 400,
    },
    'ImageNotFound': {
        'message': 'Imagem não encontrada',
        'status': 404,
    },
}

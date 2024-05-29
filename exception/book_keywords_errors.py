errors = {
    'BookKeywordDoesntExists': {
        'message': 'Essa palavra chave não existe',
        'status': 404,
    },
    'BookDoesntOwnThisKeyword': {
        'message': 'Essa palavra chave não pertence à esse livro',
        'status': 401,
    },
    'BookMustHaveAtLeastOneKeyword': {
        'message': 'O livro deve ter pelo menos uma palavra chave',
        'status': 400,
    },
}

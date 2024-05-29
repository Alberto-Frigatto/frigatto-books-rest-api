errors = {
    'BookKindAlreadyExists': {
        'message': 'Esse tipo de livro já existe',
        'status': 409,
    },
    'BookKindDoesntExists': {
        'message': 'Esse tipo de livro não existe',
        'status': 404,
    },
    'ThereAreLinkedBooksWithThisBookKind': {
        'message': 'Esse tipo de livro não pode ser apagado, pois há livros desse tipo',
        'status': 409,
    },
}

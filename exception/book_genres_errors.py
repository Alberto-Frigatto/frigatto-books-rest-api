errors = {
    'BookGenreAlreadyExists': {
        'message': 'Esse gênero de livro já existe',
        'status': 409,
    },
    'BookGenreDoesntExists': {
        'message': 'Esse gênero de livro não existe',
        'status': 404,
    },
    'ThereAreLinkedBooksWithThisBookGenre': {
        'message': 'Esse gênero de livro não pode ser apagado, pois há livros desse tipo',
        'status': 409,
    },
}

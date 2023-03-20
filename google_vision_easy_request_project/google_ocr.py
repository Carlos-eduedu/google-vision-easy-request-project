import base64
import json

import requests


def ocr_google_api(paths_images: list, api_key: str) -> str:
    """Essa função faz a requisição para a API do Google Vision e retorna o texto extraído das imagens.

    Args:
        paths_images (list): Caminhos das imagens que serão extraídas as informações.
        api_key (str): Chave da API do Google Vision.

    Returns:
        str: Texto extraído das imagens.
    """

    def __get_base64(path_image: str) -> str:
        """Essa função retorna a imagem em base64.

        Args:
            path_image (str): Caminho da imagem.

        Returns:
            str: Imagem em base64.
        """
        try:
            with open(path_image, 'rb') as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except FileNotFoundError:
            raise FileNotFoundError(f'Arquivo não encontrado: {path_image}')

    def __get_request_body(base64_images: list) -> dict:
        """Essa função retorna o corpo da requisição para a API do Google Vision.

        Args:
            base64_images (list): Lista com as imagens em base64.

        Returns:
            dict: Corpo da requisição.
        """
        data = {'requests': []}
        for base64_image in base64_images:
            data['requests'].append(
                {
                    'image': {'content': base64_image},
                    'features': [{'type': 'TEXT_DETECTION'}],
                }
            )
        return data

    def __get_response_text(response: dict) -> str:
        """Essa função retorna o texto extraído das imagens.

        Args:
            response (dict): Resposta da API do Google Vision.

        Returns:
            str: Texto extraído das imagens.
        """

        def __remove_duplicate_words(words: list) -> list:
            """Essa função remove as palavras duplicadas.

            Args:
                words (list): Lista com as palavras.

            Returns:
                list: Lista com as palavras sem duplicadas.
            """
            words_without_duplicate = []
            for word in words:
                if word not in words_without_duplicate:
                    words_without_duplicate.append(word)
            return words_without_duplicate

        text = ''
        words = []
        try:
            for response in response.json()['responses']:
                try:
                    for index in range(len(response['textAnnotations'])):
                        word = response['textAnnotations'][index][
                            'description'
                        ]

                        if '\n' in word:
                            for w in word.split('\n'):
                                words.append(w)
                        else:
                            words.append(word)
                except KeyError:
                    raise KeyError(
                        'Não foi possível extrair o texto das imagens.'
                    )
        except json.decoder.JSONDecodeError:
            raise json.decoder.JSONDecodeError(
                'Não foi possível fazer a requisição.'
            )
        except KeyError:
            raise KeyError('Não foi possível fazer a requisição.')

        words = __remove_duplicate_words(words)

        for word in words:
            text += f'{word} '

        return text

    base64_images = []

    for path_image in paths_images:
        base64_images.append(__get_base64(path_image))

    data = __get_request_body(base64_images)
    url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'

    return __get_response_text(requests.post(url=url, data=json.dumps(data)))

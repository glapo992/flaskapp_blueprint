#language support
# import the function _() that acts like a wrapper arpund the text to translate, lazy_gettext() does the same but waits an http request before transalte the text
from flask import request

from flask import jsonify
from app.translate import translate

from app.translation import bp



@bp.route('/translate', methods=['POST'])
def translate_text(): 
    return jsonify({'text':translate(
                                        request.form['text'],
                                        request.form['source_language'],
                                        request.form['dest_language'])})

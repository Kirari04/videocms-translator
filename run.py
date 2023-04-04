import uuid
from flask import Flask, request
import re
import pysubs2
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

modelPath = './nllb-200-distilled-600M'
cache = dict()
app = Flask(__name__)


@app.get('/translate')
def get_translate():
    text = request.args.get('text')
    src_lang = request.args.get('src_lang')
    tgt_lang = request.args.get('tgt_lang')
    return translate(text, src_lang, tgt_lang)


@app.post('/translate')
def post_translate():
    text = request.form.get('text')
    src_lang = request.form.get('src_lang')
    tgt_lang = request.form.get('tgt_lang')
    return translate(text, src_lang, tgt_lang)


@app.post('/translate/subtitle')
def post_translate_sub():
    text = request.form.get('text')
    subtype = request.form.get('subtype')
    src_lang = request.form.get('src_lang')
    tgt_lang = request.form.get('tgt_lang')

    tmpSubFile = "{}.{}".format(uuid.uuid5(uuid.NAMESPACE_URL, text), subtype)
    f = open(tmpSubFile, "w")
    f.write(text)
    f.close()

    subtitles = pysubs2.load(path=tmpSubFile)
    for subtitle in subtitles:
        description_pattern = re.compile("^(\[|\()((?!(\]|\))$).*)(\]|\))$")
        if description_pattern.match(subtitle.text):
            # is audio description
            subtitle.text = "[{}]".format(
                translate(
                    description_pattern.sub("\\2", subtitle.text),
                    src_lang,
                    tgt_lang
                ),
            )
        else:
            # is caption
            subtitle.text = translate(subtitle.text, src_lang, tgt_lang)
    subtitles.save(tmpSubFile)

    f = open(tmpSubFile, "r")
    returnStr = f.read()
    f.close()
    return returnStr


def translate(text, src_lang, tgt_lang):

    text_hash = hash(text)
    cacheKey = "{}-to-{}__{}".format(src_lang, tgt_lang, text_hash)

    if cacheKey not in cache:
        tokenizer = AutoTokenizer.from_pretrained(modelPath)
        model = AutoModelForSeq2SeqLM.from_pretrained(modelPath)
        translator = pipeline('translation', model=model, tokenizer=tokenizer,
                              src_lang=src_lang, tgt_lang=tgt_lang,  max_length=400)
        translatedText = translator(text)[0]['translation_text']
        cache[cacheKey] = translatedText
        return translatedText
    else:
        return cache[cacheKey]


@app.errorhandler(Exception)
def exception_handler(error):
    print(error)
    return "Internal Server Error", 500


@app.errorhandler(404)
def exception_handler(error):
    return "Not Found", 404


@app.errorhandler(400)
def exception_handler(error):
    return "Bad Request", 400


app.run(host="0.0.0.0", port=5000)

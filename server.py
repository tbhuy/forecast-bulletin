from sparkinclimate.api import app
import sparkinclimate.api.places
import sparkinclimate.api.facts
import sparkinclimate.api.pdf
import sparkinclimate.api.dates

if __name__ == '__main__':
    # app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'
    # app.config['RESTPLUS_VALIDATE'] = True
    app.config['RESTPLUS_MASK_SWAGGER'] = False
    # app.config['ERROR_404_HELP'] = False

    app.run(debug=True, host='0.0.0.0')
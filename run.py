from app.routes import app
from app.models import db

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bus_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)

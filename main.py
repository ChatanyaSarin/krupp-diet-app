from flask import Flask, render_template, request
from workflow import generate_daily_meals

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    meal_plan = None
    error = None

    if request.method == 'POST':
        context = {
            'biomarker_summary': request.form.get('biomarker_summary', ''),
            'taste_summary': request.form.get('taste_summary', ''),
            'day_macro_goals': request.form.get('day_macro_goals', '')
        }
        try:
            meal_plan = generate_daily_meals(context)
        except Exception as e:
            error = str(e)

    return render_template('index.html', meal_plan=meal_plan, error=error)

if __name__ == '__main__':
    app.run(debug=True)
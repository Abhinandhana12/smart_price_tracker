import numpy as np
from sklearn.linear_model import LinearRegression

def predict_price(history):
    """
    Predict the next price using Linear Regression on historical data.
    history: list of dicts with 'price' and 'recorded_at'
    Returns predicted price (float) rounded to 2 decimal places.
    """
    if len(history) < 2:
        return None

    prices = [h['price'] for h in history]
    X = np.array(range(len(prices))).reshape(-1, 1)
    y = np.array(prices)

    model = LinearRegression()
    model.fit(X, y)

    next_index = np.array([[len(prices)]])
    predicted = model.predict(next_index)[0]

    return round(float(predicted), 2)

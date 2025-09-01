from flask import Flask, render_template, request, send_from_directory, url_for
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Create static folder if not exists
if not os.path.exists("static"):
    os.makedirs("static")


@app.route("/", methods=["GET", "POST"])
def predict():
    plot_path_ema_20_50 = None
    plot_path_ema_100_200 = None
    plot_path_prediction = None
    data_desc = None
    dataset_link = None
    predicted_price = None   # <--- new variable

    if request.method == "POST":
        ticker = request.form["stock"].strip().upper()

        # Fetch stock data
        df = yf.download(ticker, start="2000-01-01", end="2024-11-30")

        if not df.empty:
            # Save dataset
            dataset_path = os.path.join("static", f"{ticker}_data.csv")
            df.to_csv(dataset_path)
            dataset_link = dataset_path

            # Calculate EMAs
            df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
            df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
            df["EMA100"] = df["Close"].ewm(span=100, adjust=False).mean()
            df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

            # --- Plot EMA 20 & 50 ---
            plt.figure(figsize=(10, 6))
            plt.plot(df["Close"], label="Closing Price", color="blue")
            plt.plot(df["EMA20"], label="EMA 20", color="red")
            plt.plot(df["EMA50"], label="EMA 50", color="green")
            plt.legend()
            plt.title("Closing Price vs Time (20 & 50 Days EMA)")
            ema_20_50_path = os.path.join("static", "ema_20_50.png")
            plt.savefig(ema_20_50_path)
            plt.close()
            plot_path_ema_20_50 = ema_20_50_path

            # --- Plot EMA 100 & 200 ---
            plt.figure(figsize=(10, 6))
            plt.plot(df["Close"], label="Closing Price", color="blue")
            plt.plot(df["EMA100"], label="EMA 100", color="orange")
            plt.plot(df["EMA200"], label="EMA 200", color="purple")
            plt.legend()
            plt.title("Closing Price vs Time (100 & 200 Days EMA)")
            ema_100_200_path = os.path.join("static", "ema_100_200.png")
            plt.savefig(ema_100_200_path)
            plt.close()
            plot_path_ema_100_200 = ema_100_200_path

            # --- Prediction Chart (Dummy: EMA20 as prediction) ---
            plt.figure(figsize=(10, 6))
            plt.plot(df["Close"], label="Original Closing Price", color="blue")
            plt.plot(df["EMA20"], label="Predicted Trend (EMA20)", color="red")
            plt.legend()
            plt.title("Prediction vs Original Trend")
            prediction_path = os.path.join("static", "stock_prediction.png")
            plt.savefig(prediction_path)
            plt.close()
            plot_path_prediction = prediction_path

            # --- Descriptive Stats ---
            data_desc = df.describe().to_html(classes="table table-striped", border=0)

            # --- Predicted Next Closing Price ---
            last_close = df["Close"].iloc[-1]
            last_ema20 = df["EMA20"].iloc[-1]
            # Simple average of last close + EMA20 (dummy logic)
            predicted_price = round((last_close + last_ema20) / 2, 2)

    return render_template(
        "index.html",
        plot_path_ema_20_50=plot_path_ema_20_50,
        plot_path_ema_100_200=plot_path_ema_100_200,
        plot_path_prediction=plot_path_prediction,
        data_desc=data_desc,
        dataset_link=dataset_link,
        predicted_price=predicted_price   # <--- sending to HTML
    )


# CSV download route
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory("static", filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)

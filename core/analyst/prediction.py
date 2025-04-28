from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import numpy as np
import matplotlib 
matplotlib.use('Agg')  # Use a non-GUI backend for matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import locale
from scipy.interpolate import BarycentricInterpolator
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import pytz
import os

locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

# Timezone Asia/Jakarta
TIMEZONE = pytz.timezone('Asia/Jakarta')

def convert_time_to_numeric(df):
    start_time = df['waktu'].min()
    return df.assign(time_numeric=df['waktu'].apply(lambda x: (x - start_time).total_seconds() / 3600))

def interpolasi_newton(df, num_points=100):
    x = df['time_numeric'].values
    y = df['nilai'].values
    interp_func = BarycentricInterpolator(x, y)
    x_new = np.linspace(min(x), max(x), num_points)
    y_new = interp_func(x_new)
    return x_new, y_new, interp_func

def regresi_linear(df, future_hours=24):
    X = df['time_numeric'].values.reshape(-1, 1)
    y = df['nilai'].values
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    last_time = df['time_numeric'].max()
    future_times = np.linspace(last_time, last_time + future_hours, 50)
    y_future = model.predict(future_times.reshape(-1, 1))
    return X.flatten(), y_pred, future_times, y_future, model

def prediksi_nilai(model, tanggal_input, start_time):
    time_diff = (tanggal_input - start_time).total_seconds() / 3600
    return model.predict([[time_diff]])[0]

def prediksi_nilai_newton(interp_func, tanggal_input, start_time):
    time_diff = (tanggal_input - start_time).total_seconds() / 3600
    return interp_func(time_diff)

def tampilkan_grafik_regresi(df, x_reg, y_reg, future_x, future_y, pred_time, pred_value, start_time):
    reg_dates = [start_time + timedelta(hours=h) for h in x_reg]
    future_dates = [start_time + timedelta(hours=h) for h in future_x]

    plt.figure(figsize=(10, 6))
    plt.plot(df['waktu'], df['nilai'], 'o-', label='Data Asli', markersize=3)
    plt.plot(reg_dates, y_reg, '-', label='Regresi Linear')
    plt.plot(future_dates, future_y, '--', label='Prediksi Regresi')
    plt.plot(pred_time, pred_value, 'r*', markersize=15, label=f'Prediksi: {pred_value:.2f}')

    plt.title(f'Prediksi dengan Regresi Linear pada {pred_time}')
    plt.xlabel('Waktu')
    plt.ylabel('Nilai Popularitas')
    plt.legend()
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.tight_layout()

    image_path = os.path.join('core', 'static', 'images', 'analisis_hari_bumi_simple.png')
    plt.savefig(image_path)
    plt.close()

def tampilkan_grafik_interpolasi(df, x_interp, y_interp, pred_time, pred_value, start_time):
    interp_dates = [start_time + timedelta(hours=h) for h in x_interp]

    plt.figure(figsize=(12, 6))
    plt.plot(df['waktu'], df['nilai'], 'o-', label='Data Asli', markersize=3)
    plt.plot(interp_dates, y_interp, ':', label='Interpolasi Newton', linewidth=2)
    plt.plot(pred_time, pred_value, 'r*', markersize=15, label=f'Prediksi: {pred_value:.2f}')

    plt.title(f'Prediksi dengan Interpolasi Newton pada {pred_time}')
    plt.xlabel('Waktu')
    plt.ylabel('Nilai Popularitas')
    plt.legend()
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.tight_layout()
    
    image_path = os.path.join('core', 'static', 'images', 'analisis_hari_bumi_simple.png')
    plt.savefig(image_path)
    plt.close()

# Main view to handle logic
def analisis_view(request):
    try:
        df = pd.read_csv('hari_bumi.csv')
        df['waktu'] = pd.to_datetime(df['waktu'])
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    df_numeric = convert_time_to_numeric(df)
    start_time = df['waktu'].min()

    x_reg, y_reg, future_x, future_y, linear_model = regresi_linear(df_numeric, future_hours=24)
    x_newton, y_newton, interp_func = interpolasi_newton(df_numeric)

    # Handling form submission for user input
    if request.method == 'POST':
        selected_date = request.POST.get('datetime')
        try:
            naive_datetime = datetime.strptime(selected_date, '%Y-%m-%dT%H:%M')
            tanggal_input = TIMEZONE.localize(naive_datetime)
            # print("Input tanggal: " + tanggal_input.strftime("%A, %d %B %Y"))

            min_date = df['waktu'].min()
            max_date = df['waktu'].max()

            if min_date <= tanggal_input <= max_date:
                nilai_prediksi = prediksi_nilai_newton(interp_func, tanggal_input, start_time)
                print(f"\n[INTERPOLASI] Prediksi nilai pada {tanggal_input}: {nilai_prediksi:.2f}")
                tampilkan_grafik_interpolasi(df, x_newton, y_newton, tanggal_input, nilai_prediksi, start_time)
            else:
                nilai_prediksi = prediksi_nilai(linear_model, tanggal_input, start_time)
                print(f"\n[REGRESI] Prediksi nilai pada {tanggal_input}: {nilai_prediksi:.2f}")
                tampilkan_grafik_regresi(df, x_reg, y_reg, future_x, future_y, tanggal_input, nilai_prediksi, start_time)


            # Show results in a JSON format
            # return JsonResponse({"prediksi": nilai_prediksi}, status=200)
            return render(request, 'index.html', {
                'start_time': df['waktu'].min(),
                'end_time': df['waktu'].max(),
                'max_value': df['nilai'].max(),
                'max_time': df.loc[df['nilai'].idxmax(), 'waktu'],
                'equation': f"y = {linear_model.coef_[0]:.4f}x + {linear_model.intercept_:.4f}",
                'last_pred': linear_model.predict([[df_numeric['time_numeric'].max()]])[0],
                'future_pred': linear_model.predict([[df_numeric['time_numeric'].max() + 24]])[0],
                'scroll_to_graph': True,
                'selected_date': selected_date,
                'prediction_score': round(nilai_prediksi, 2),
                'locale_time': tanggal_input.strftime("%A  tanggal %d %B %Y - %H:%M"),
            })
        except ValueError as e:
            return JsonResponse({"error": "Input tidak valid."}, status=400)

    # Rendering the HTML page
    return render(request, 'index.html', {
        'start_time': df['waktu'].min(),
        'end_time': df['waktu'].max(),
        'max_value': df['nilai'].max(),
        'max_time': df.loc[df['nilai'].idxmax(), 'waktu'],
        'equation': f"y = {linear_model.coef_[0]:.4f}x + {linear_model.intercept_:.4f}",
        'last_pred': linear_model.predict([[df_numeric['time_numeric'].max()]])[0],
        'future_pred': linear_model.predict([[df_numeric['time_numeric'].max() + 24]])[0],
    })

import io

import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import plotly.express as px

# Настройка конфигурации страницы
st.set_page_config(page_title="Прогноз оттока клиентов", layout="wide")
st.title("📊 Прогноз оттока клиентов")

# Адрес FastAPI-сервера (по умолчанию локально на порту 8000)
# API_URL = "http://backend:8000"

API_URL = "http://localhost:8000"

# Разделение на вкладки
tab1, tab2 = st.tabs(["📤 Загрузка данных", "📈 Результаты предсказаний"])

error_message = ""

with tab1:
    st.markdown(
        """
    ### 📁 Инструкция
    Загрузите CSV-файл с данными клиентов банка.  
    Обязательные столбцы указаны ниже. Можно загрузить файл с большим числом столбцов — лишние будут автоматически удалены в ходе предобработки. 
    - `CustomerId`
    - `Geography` (значения: France, Germany, Spain)
    - `CreditScore`, `Age`, `Tenure`, `Balance`, `NumOfProducts`, `EstimatedSalary` (числовые); `HasCrCard`, `IsActiveMember` (бинарные: 0 или 1)
    - `Gender` (значения: Male или Female, либо можно передать уже бинарный `Gender_Male`)
    """
    )

    # Пример данных для загрузки
    sample_data = pd.DataFrame(
        {
            "CustomerId": [15634602, 15647311, 15619304, 15701354, 15601346],
            "Geography": ["France", "Spain", "France", "Germany", "France"],
            "CreditScore": [619, 608, 502, 699, 850],
            "Age": [42, 41, 42, 39, 43],
            "Tenure": [2, 1, 8, 1, 2],
            "Balance": [0.00, 83807.86, 159660.80, 0.00, 125510.82],
            "NumOfProducts": [1, 1, 3, 2, 1],
            "HasCrCard": [1, 0, 1, 1, 1],
            "IsActiveMember": [1, 1, 0, 0, 1],
            "EstimatedSalary": [101348.88, 112542.58, 113931.57, 93826.63, 79084.10],
            "Gender": ["Male", "Female", "Female", "Female", "Male"],
        }
    )
    st.markdown("#### Пример данных:")
    st.dataframe(sample_data)

    # Разрешаем загружать любой тип файла
    uploaded_file = st.file_uploader("🔼 Загрузите CSV-файл")

    if uploaded_file is not None:
        # Проверяем, что имя файла заканчивается на .csv
        if not uploaded_file.name.lower().endswith(".csv"):
            error_message = "Ошибка: Пожалуйста, загрузите файл в формате CSV!"
            st.error(error_message)
            st.stop()  # Останавливаем выполнение, чтобы не обрабатывать неверный файл

    if uploaded_file:
        try:
            data = pd.read_csv(uploaded_file)

            # Обязательные признаки без учета пола
            model_features = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts',
                              'HasCrCard', 'IsActiveMember', 'EstimatedSalary']

            missing_features = [col for col in model_features if col not in data.columns]

            # Проверяем наличие либо 'Gender_Male', либо 'Gender'
            if 'Gender_Male' not in data.columns and 'Gender' not in data.columns:
                missing_features.append('Gender_Male/Gender')

            if missing_features:
                error_message = f"Отсутствуют обязательные признаки: {missing_features}"
                st.error(error_message)

            else:
                st.success("✅ Данные успешно загружены!")

                st.markdown("### 🔍 Часть загруженных данных:")
                st.dataframe(data.sample(3))

                # Минимальный CSS для "карточек" без тени
                st.markdown(
                    """
                    <style>
                    .stat-box {
                        background-color: #FFFFFF;
                        padding: 0.25rem;
                        border-radius: 0.25rem;
                        margin-bottom: 1rem;
                    }
                    .stat-box h5 {
                        margin: 0 0 0.5rem 0;
                        font-weight: 600;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("## 📊 Статистика по данным")

                # --- ПЕРВЫЙ РЯД (3 колонки) ---
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)

                    st.markdown(
                        "<h5>📌 Распределение клиентов по странам</h5>",
                        unsafe_allow_html=True,
                    )
                    geo_stats = (
                        data["Geography"]
                        .value_counts()
                        .rename_axis("Страна")
                        .reset_index(name="Количество")
                    )
                    st.dataframe(geo_stats)

                    fig = px.bar(geo_stats, x='Страна', y='Количество', title='Распределение клиентов по странам')

                    # Увеличиваем названия осей и шрифт подписей на осях
                    fig.update_xaxes(
                        title_text='Страна',
                        title_font=dict(size=16, color='black'),  # Размер шрифта названия оси X
                        tickfont=dict(size=14)  # Размер шрифта значений делений на оси X
                    )
                    fig.update_yaxes(
                        title_text='Количество',
                        title_font=dict(size=16, color='black'),  # Размер шрифта названия оси Y
                        tickfont=dict(size=14)  # Размер шрифта значений делений на оси Y
                    )
                    fig.update_layout(
                        width=410,
                        height=410,
                        title_font=dict(size=18),
                    )

                    st.plotly_chart(fig)

                    st.markdown("</div>", unsafe_allow_html=True)

                with col2:
                    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
                    st.markdown(
                        "<h5>📌 Распределение клиентов по полу</h5>",
                        unsafe_allow_html=True,
                    )

                    data['Gender'] = data['Gender'].replace({
                        'Male': 'Мужчины',
                        'Female': 'Женщины'
                    })

                    gender_stats = (
                        data["Gender"]
                        .value_counts()
                        .rename_axis("Пол")
                        .reset_index(name="Количество")
                    )
                    st.dataframe(gender_stats)

                    for _ in range(2):
                        st.write("")

                    fig = px.pie(gender_stats,
                                 names='Пол',
                                 values='Количество',
                                 title='Распределение клиентов по полу')

                    fig.update_traces(
                        textfont=dict(size=18)
                    )
                    fig.update_layout(
                        width=410,
                        height=410,
                        title_font=dict(size=18),
                        legend=dict(font=dict(size=14))
                    )

                    st.plotly_chart(fig)

                    st.markdown("</div>", unsafe_allow_html=True)

                with col3:
                    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
                    st.markdown(
                        "<h5>📌 Статистика по возрасту</h5>", unsafe_allow_html=True
                    )
                    age_stats = data["Age"].describe()[["mean", "min", "max"]]
                    age_stats_df = age_stats.to_frame().T.rename(
                        columns={"mean": "Среднее", "min": "Минимум", "max": "Максимум"}
                    )
                    st.dataframe(age_stats_df)

                    for _ in range(4):
                        st.write("")

                    fig = px.histogram(data, x="Age", nbins=20, title="Распределение возраста клиентов")

                    # Увеличиваем названия осей и шрифт подписей на осях
                    fig.update_xaxes(
                        title_text='Возраст',
                        title_font=dict(size=16, color='black'),  # Размер шрифта названия оси X
                        tickfont=dict(size=14)  # Размер шрифта значений делений на оси X
                    )
                    fig.update_yaxes(
                        title_text='Количество',
                        title_font=dict(size=16, color='black'),  # Размер шрифта названия оси Y
                        tickfont=dict(size=14)  # Размер шрифта значений делений на оси Y
                    )
                    fig.update_layout(
                        width=410,
                        height=410,
                        title_font=dict(size=18),
                    )

                    st.plotly_chart(fig)

                    st.markdown("</div>", unsafe_allow_html=True)

                # --- ВТОРОЙ РЯД (3 колонки) ---
                col4, col5, col6 = st.columns(3)
                with col4:
                    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
                    st.markdown(
                        "<h5>📌 Распределение клиентов по количеству продуктов</h5>",
                        unsafe_allow_html=True,
                    )
                    prod_stats = (
                        data["NumOfProducts"]
                        .value_counts()
                        .rename_axis("Кол-во продуктов")
                        # .reset_index(name="Количество")
                    )
                    prod_stats.rename('Количество',inplace=True)

                    st.dataframe(prod_stats)

                    fig = px.bar(x=prod_stats.index, y=prod_stats.values,
                                 title='Распределение клиентов по кол-ву продуктов')

                    # Увеличиваем названия осей и шрифт подписей на осях
                    fig.update_xaxes(
                        title_text='Кол-во продуктов',
                        title_font=dict(size=16, color='black'),  # Размер шрифта названия оси X
                        tickfont=dict(size=14)  # Размер шрифта значений делений на оси X
                    )
                    fig.update_yaxes(
                        title_text='Количество',
                        title_font=dict(size=16, color='black'),  # Размер шрифта названия оси Y
                        tickfont=dict(size=14)  # Размер шрифта значений делений на оси Y
                    )
                    fig.update_layout(
                        width=410,
                        height=410,
                        title_font=dict(size=18),
                    )

                    st.plotly_chart(fig)

                    st.markdown("</div>", unsafe_allow_html=True)

                with col5:
                    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
                    st.markdown(
                        "<h5>📌 Клиенты по наличию кредитной карты</h5>",
                        unsafe_allow_html=True,
                    )
                    card_stats = (
                        data["HasCrCard"]
                        .replace({1: "1 (Есть карта)", 0: "0 (Нет карты)"})
                        .value_counts()
                        .rename_axis("Статус карты")
                        .reset_index(name="Количество")
                    )
                    st.dataframe(card_stats)

                    for _ in range(6):
                        st.write("")

                    fig = px.pie(card_stats, names='Статус карты', values='Количество',
                                 title='Клиенты по наличию кредитной карты')

                    fig.update_traces(
                        textfont=dict(size=18)
                    )
                    fig.update_layout(
                        width=410,
                        height=410,
                        title_font=dict(size=18),
                        legend=dict(font=dict(size=14))
                    )

                    st.plotly_chart(fig)

                    st.markdown("</div>", unsafe_allow_html=True)

                with col6:
                    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
                    st.markdown(
                        "<h5>📌 Клиенты по активности</h5>", unsafe_allow_html=True
                    )
                    active_stats = (
                        data["IsActiveMember"]
                        .replace({1: "1 (Активный)", 0: "0 (Не активный)"})
                        .value_counts()
                        .rename_axis("Активность")
                        .reset_index(name="Количество")
                    )
                    st.dataframe(active_stats)

                    for _ in range(6):
                        st.write("")

                    fig = px.pie(active_stats, names='Активность', values='Количество', title='Клиенты по активности')

                    fig.update_traces(
                        textfont=dict(size=18)
                    )
                    fig.update_layout(
                        width=410,
                        height=410,
                        title_font=dict(size=18),
                        legend=dict(font=dict(size=14))
                    )

                    st.plotly_chart(fig)

                    st.markdown("</div>", unsafe_allow_html=True)

                # --- ТРЕТИЙ РЯД (3 колонки) для CreditScore, Tenure, Balance ---
                col7, col8, col9 = st.columns(3)
                with col7:
                    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
                    st.markdown(
                        "<h5>📌 Статистика по кредитному рейтингу</h5>",
                        unsafe_allow_html=True,
                    )
                    credit_stats = data["CreditScore"].describe()[["mean", "min", "max"]]
                    credit_stats_df = credit_stats.to_frame().T.rename(
                        columns={"mean": "Среднее", "min": "Минимум", "max": "Максимум"}
                    )
                    st.dataframe(credit_stats_df)

                    fig = px.histogram(data, x="CreditScore", nbins=20, title="Распределение кредитного рейтинга")

                    # Увеличиваем названия осей и шрифт подписей на осях
                    fig.update_xaxes(
                        title_text='Кредитный рейтинг',
                        title_font=dict(size=16, color='black'),  # Размер шрифта названия оси X
                        tickfont=dict(size=14)  # Размер шрифта значений делений на оси X
                    )
                    fig.update_yaxes(
                        title_text='Количество',
                        title_font=dict(size=16, color='black'),  # Размер шрифта названия оси Y
                        tickfont=dict(size=14)  # Размер шрифта значений делений на оси Y
                    )
                    fig.update_layout(
                        width=410,
                        height=410,
                        title_font=dict(size=18),
                    )

                    st.plotly_chart(fig)

                    st.markdown("</div>", unsafe_allow_html=True)

                with col8:
                    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
                    st.markdown(
                        "<h5>📌 Статистика по количеству лет в банке</h5>",
                        unsafe_allow_html=True,
                    )
                    tenure_stats = data["Tenure"].describe()[["mean", "min", "max"]]
                    tenure_stats_df = tenure_stats.to_frame().T.rename(
                        columns={"mean": "Среднее", "min": "Минимум", "max": "Максимум"}
                    )
                    st.dataframe(tenure_stats_df)

                    fig = px.histogram(data, x="Tenure", nbins=10, title="Распределение количества лет в банке")

                    # Увеличиваем названия осей и шрифт подписей на осях
                    fig.update_xaxes(
                        title_text='Кол-во лет в банке',
                        title_font=dict(size=16, color='black'),  # Размер шрифта названия оси X
                        tickfont=dict(size=14)  # Размер шрифта значений делений на оси X
                    )
                    fig.update_yaxes(
                        title_text='Количество',
                        title_font=dict(size=16, color='black'),  # Размер шрифта названия оси Y
                        tickfont=dict(size=14)  # Размер шрифта значений делений на оси Y
                    )
                    fig.update_layout(
                        width=410,
                        height=410,
                        title_font=dict(size=18),
                    )

                    st.plotly_chart(fig)

                    st.markdown("</div>", unsafe_allow_html=True)

                with col9:
                    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
                    st.markdown(
                        "<h5>📌 Статистика по балансу на счете</h5>",
                        unsafe_allow_html=True,
                    )
                    balance_stats = data["Balance"].describe()[["mean", "min", "max"]]
                    balance_stats_df = balance_stats.to_frame().T.rename(
                        columns={"mean": "Среднее", "min": "Минимум", "max": "Максимум"}
                    )
                    st.dataframe(balance_stats_df)

                    fig = px.histogram(data, x="Balance", nbins=20, title="Распределение баланса на счете")

                    # Увеличиваем названия осей и шрифт подписей на осях
                    fig.update_xaxes(
                        title_text='Баланс на счете',
                        title_font=dict(size=16, color='black'),  # Размер шрифта названия оси X
                        tickfont=dict(size=14)  # Размер шрифта значений делений на оси X
                    )
                    fig.update_yaxes(
                        title_text='Количество',
                        title_font=dict(size=16, color='black'),  # Размер шрифта названия оси Y
                        tickfont=dict(size=14)  # Размер шрифта значений делений на оси Y
                    )
                    fig.update_layout(
                        width=410,
                        height=410,
                        title_font=dict(size=18),
                    )

                    st.plotly_chart(fig)

                    st.markdown("</div>", unsafe_allow_html=True)

                st.session_state[
                    "raw_data"
                ] = data  # сохраняем данные для дальнейшей обработки

        except Exception as e:
            st.error(f"Ошибка чтения файла: {e}")

with tab2:
    if "raw_data" not in st.session_state and error_message == "":
        st.warning("⚠️ Сначала загрузите данные во вкладке '📤 Загрузка данных'")
    elif error_message != "":
        st.warning(error_message)
    else:
        data = st.session_state["raw_data"]

        # Формируем пакет данных для отправки (список словарей)
        payload = {"clients": data.to_dict(orient="records")}

        try:
            response = requests.post(f"{API_URL}/predict_batch", json=payload)
            if response.status_code == 200:
                results = response.json()
            else:
                st.error(f"Ошибка: {response.text}")
                results = None
        except Exception as e:
            st.error(f"Ошибка запроса: {e}")
            results = None

        if results:
            final_results = pd.DataFrame(results)
            st.success("✅ Предсказания завершены!")

            # Возможность скачивания результатов
            csv = final_results.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Скачать результат (CSV)",
                data=csv,
                file_name="churn_predictions.csv",
                mime="text/csv",
                help="Скачать результат предсказаний клиентов в формате .csv"
            )

            # Две равные колонки
            col1, col2 = st.columns(2)

            # Определяем словарь для переименования столбцов
            rename_dict = {
                "CustomerId": "ID клиента",
                "Geography": "Страна",
                "prediction": "Предсказание",
                "churn_probability": "Вероятность оттока",
            }

            # Разбиваем на колонки
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Результаты предсказаний клиентов")
                st.markdown("**Легенда:** 0 — клиент останется, 1 — клиент уйдёт")
                # Создаём копию с переименованными столбцами
                final_renamed = final_results.rename(columns=rename_dict)
                st.dataframe(final_renamed)

            with col2:
                st.markdown("### Топ-10 клиентов с высоким риском оттока")
                st.markdown("**Легенда:** 0 — клиент останется, 1 — клиент уйдёт")
                top_risk = (
                    final_results[final_results["prediction"] == 1]
                    .sort_values("churn_probability", ascending=False)
                    .head(10)
                )
                top_risk_renamed = top_risk.rename(columns=rename_dict)
                st.dataframe(top_risk_renamed)

            st.markdown("### Распределение предсказаний по оттоку")
            churn_counts = final_results["prediction"].value_counts().sort_index()

            # Увеличиваем размер фигуры
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.bar(["Останется", "Уйдёт"], churn_counts, color=["green", "red"])
            ax.set_ylabel("Количество клиентов")

            # Не используем tight layout, чтобы не обрезать поля
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            st.image(buf)
            plt.close(fig)

            # --- Дополнительная аналитика ---
            st.markdown("## Дополнительная аналитика")

            if "raw_data" in st.session_state:
                raw_data = st.session_state["raw_data"]
                # Объединяем предсказания с исходными данными по CustomerId
                merged = pd.merge(
                    final_results,
                    raw_data[
                        [
                            "CustomerId",
                            "Age",
                            "NumOfProducts",
                            "IsActiveMember",
                            "Balance",
                            "Gender"
                        ]
                    ],
                    on="CustomerId",
                    how="left",
                )
                # Формируем возрастные группы
                merged["Возрастная группа"] = pd.cut(
                    merged["Age"],
                    bins=[0, 30, 40, 50, 60, 100],
                    labels=["<30", "30-40", "40-50", "50-60", "60+"],
                )

                # Средняя вероятность ухода по странам
                geo_avg = merged.groupby("Geography")["churn_probability"].mean()
                geo_avg = geo_avg.rename("Средняя вероятность ухода")
                geo_avg = geo_avg.rename(index={'France': "Франция", 'Germany': "Германия", 'Spain': 'Испания'})
                geo_avg.index.rename("Страна", inplace=True)

                # Средняя вероятность ухода по возрастным группам
                age_avg = merged.groupby("Возрастная группа", observed=False)["churn_probability"].mean()
                age_avg = age_avg.rename("Средняя вероятность ухода")
                age_avg.index.rename("Возрастная группа", inplace=True)

                # Средняя вероятность ухода по количеству продуктов
                product_avg = merged.groupby("NumOfProducts")["churn_probability"].mean()
                product_avg = product_avg.rename("Средняя вероятность ухода")
                product_avg.index.name = 'Кол-во продуктов'

                # Средняя вероятность ухода по активности
                active_avg = merged.groupby("IsActiveMember")["churn_probability"].mean()
                active_avg = active_avg.rename("Средняя вероятность ухода")
                active_avg = active_avg.rename(index={0: "Не активный", 1: "Активный"})
                active_avg.index.rename("Активность", inplace=True)

                # Средняя вероятность ухода по группам баланса
                bins = [-1, 0, 10000, 50000, 100000, merged["Balance"].max()]
                labels = ["0", "0-10000", "10000-50000", "50000-100000", "100000+"]
                merged["Баланс группы"] = pd.cut(merged["Balance"], bins=bins, labels=labels)
                balance_avg = merged.groupby("Баланс группы")["churn_probability"].mean()
                balance_avg = balance_avg.rename("Средняя вероятность ухода")
                balance_avg.index.rename("Баланс", inplace=True)

                # Средняя вероятность ухода по полу
                gender_avg = merged.groupby("Gender")["churn_probability"].mean()
                gender_avg = gender_avg.rename("Средняя вероятность ухода")
                gender_avg = gender_avg.rename(index={'Female': "Женский", 'Male': "Мужской"})
                gender_avg.index.rename("Пол", inplace=True)

                # Приведение индексов к строковому типу для графиков (если требуется)
                age_avg.index = age_avg.index.astype(str)
                balance_avg.index = balance_avg.index.astype(str)

                st.markdown(
                    '<h3 style="color: #2E86C1;">Средняя вероятность ухода</h3>',
                    unsafe_allow_html=True,
                )

                # Первый ряд: по странам, по полу, по активности
                col_avg1, col_avg2, col_avg3 = st.columns(3)
                with col_avg1:
                    st.markdown("#### По странам")
                    st.dataframe(geo_avg)
                    geo_df = geo_avg.reset_index()

                    fig = px.pie(geo_df,
                                 names='Страна',
                                 values='Средняя вероятность ухода',
                                 title='Средняя вероятность ухода по странам'
                                 )

                    fig.update_traces(
                        textfont=dict(size=18)
                    )
                    fig.update_layout(
                        width=410,
                        height=410,
                        title_font=dict(size=18),
                        legend=dict(font=dict(size=14))
                    )

                    st.plotly_chart(fig)

                with col_avg2:
                    st.markdown("#### По полу")
                    st.dataframe(gender_avg)
                    gender_df = gender_avg.reset_index()

                    for _ in range(2):
                        st.write("")

                    fig = px.pie(gender_df,
                                 names='Пол',
                                 values='Средняя вероятность ухода',
                                 title='Средняя вероятность ухода по полу'
                                 )

                    fig.update_traces(
                        textfont=dict(size=18)
                    )
                    fig.update_layout(
                        width=410,
                        height=410,
                        title_font=dict(size=18),
                        legend=dict(font=dict(size=14))
                    )

                    st.plotly_chart(fig)

                with col_avg3:
                    st.markdown("#### По активности")
                    st.dataframe(active_avg)
                    active_df = active_avg.reset_index()

                    for _ in range(2):
                        st.write("")

                    fig = px.pie(active_df,
                                 names='Активность',
                                 values='Средняя вероятность ухода',
                                 title='Средняя вероятность ухода по активности'
                                 )

                    fig.update_traces(
                        textfont=dict(size=18)
                    )
                    fig.update_layout(
                        width=410,
                        height=410,
                        title_font=dict(size=18),
                        legend=dict(font=dict(size=14))
                    )

                    st.plotly_chart(fig)

                # Второй ряд: по возрастным группам, по группам баланса, по количеству продуктов
                col_new1, col_new2, col_new3 = st.columns(3)
                with col_new1:
                    st.markdown("#### По возрастным группам")
                    st.dataframe(age_avg)
                    age_df = age_avg.reset_index()
                    fig_age = px.bar(
                        age_df,
                        x="Возрастная группа",
                        y="Средняя вероятность ухода",
                        title="Средняя вер-ть ухода по возрастным группам"
                    )
                    fig_age.update_xaxes(
                        title_text='Возрастная группа',
                        title_font=dict(size=16, color='black'),
                        tickfont=dict(size=14)
                    )
                    fig_age.update_yaxes(
                        title_text='Вероятность',
                        title_font=dict(size=16, color='black'),
                        tickfont=dict(size=14)
                    )
                    fig_age.update_layout(width=410, height=410, title_font=dict(size=18))
                    st.plotly_chart(fig_age)

                with col_new2:
                    st.markdown("#### По группам баланса")
                    st.dataframe(balance_avg)
                    balance_df = balance_avg.reset_index()
                    fig_balance = px.bar(
                        balance_df,
                        x="Баланс",
                        y="Средняя вероятность ухода",
                        title="Средняя вероятность ухода по группам баланса"
                    )
                    fig_balance.update_xaxes(
                        title_text='Баланс',
                        title_font=dict(size=16, color='black'),
                        tickfont=dict(size=14)
                    )
                    fig_balance.update_yaxes(
                        title_text='Вероятность',
                        title_font=dict(size=16, color='black'),
                        tickfont=dict(size=14)
                    )
                    fig_balance.update_layout(width=410, height=410, title_font=dict(size=18))
                    st.plotly_chart(fig_balance)

                with col_new3:
                    st.markdown("#### По количеству продуктов")
                    st.dataframe(product_avg)
                    product_df = product_avg.reset_index()

                    for _ in range(2):
                        st.write("")

                    fig_product = px.bar(
                        product_df,
                        x="Кол-во продуктов",
                        y="Средняя вероятность ухода",
                        title="Средняя вероятность ухода по кол-ву продуктов"
                    )
                    fig_product.update_xaxes(
                        title_text='Кол-во продуктов',
                        title_font=dict(size=16, color='black'),
                        tickfont=dict(size=14)
                    )
                    fig_product.update_yaxes(
                        title_text='Вероятность',
                        title_font=dict(size=16, color='black'),
                        tickfont=dict(size=14)
                    )
                    fig_product.update_layout(width=410, height=410, title_font=dict(size=18))
                    st.plotly_chart(fig_product)

                # Важность признаков по странам
                countries = ["France", "Germany", "Spain"]
                importances_list = []
                for country in countries:
                    response = requests.get(
                        f"{API_URL}/feature_importances", params={"country": country}
                    )
                    if response.status_code == 200:
                        fi = (
                            response.json()
                        )  # fi — словарь: { "Кредитный рейтинг": value, ... }
                        # Приводим значения к float, чтобы избежать проблем сериализации
                        fi = {k: float(v) for k, v in fi.items()}
                        df = pd.DataFrame(
                            {
                                "Feature": list(fi.keys()),
                                "Importance": list(fi.values()),
                            }
                        )
                        df["Country"] = country
                        importances_list.append(df)
                    else:
                        st.warning(
                            f"Не удалось получить важности признаков для {country}"
                        )

                if importances_list:
                    combined_importance = pd.concat(
                        importances_list, axis=0, ignore_index=True
                    )
                    wide_importance = combined_importance.pivot(
                        index="Feature", columns="Country", values="Importance"
                    ).fillna(0)
                    wide_importance["Mean Importance"] = wide_importance.mean(axis=1)
                    wide_importance = wide_importance.sort_values(
                        by="Mean Importance", ascending=False
                    )
                    wide_importance_for_table = wide_importance.rename(
                        columns={
                            "France": "Франция",
                            "Germany": "Германия",
                            "Spain": "Испания",
                            "Mean Importance": "Средняя важность",
                        }
                    )
                    wide_importance_for_table.index.name = "Признак"

                    st.markdown(
                        '<h3 style="color: #2E86C1;">Важность признаков по странам</h3>',
                        unsafe_allow_html=True,
                    )

                    col_feat1, col_feat2 = st.columns(2)
                    st.markdown("#### Таблица")
                    st.dataframe(wide_importance_for_table)
                    st.markdown("#### График")
                    fig3, ax3 = plt.subplots(figsize=(10, 6))
                    plot_data = wide_importance.drop(columns="Mean Importance")
                    plot_data.plot(kind="barh", stacked=True, ax=ax3, edgecolor="white")
                    ax3.set_title("Важность признаков по странам", fontsize=16)
                    ax3.set_xlabel("Важность", fontsize=14)
                    ax3.set_ylabel("Признак", fontsize=14)
                    ax3.grid(True, axis="x", linestyle="--", alpha=0.7)
                    for container in ax3.containers:
                        ax3.bar_label(
                            container,
                            fmt="%.2f",
                            label_type="center",
                            fontsize=10,
                            color="black",
                        )
                    plt.tight_layout()
                    buf3 = io.BytesIO()
                    plt.savefig(buf3, format="png", bbox_inches="tight")
                    buf3.seek(0)
                    st.image(buf3)
                    plt.close(fig3)
                else:
                    st.error(
                        "Не удалось получить данные по важности признаков ни для одной из стран."
                    )
            else:
                st.warning("Исходные данные не найдены. Загрузите данные для анализа.")
        else:
            st.warning("Неправильный тип загружаемых данных")

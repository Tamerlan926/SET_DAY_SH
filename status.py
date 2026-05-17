import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def get_insights(recs):
    if not recs: return "Нет данных."
    df = pd.DataFrame(recs)
    m = df['set'].mean()
    w = df['work_hours'].mean()
    s = df['sleep_hours'].mean()
    
    hs = df[df['sleep_hours'] >= 7.5]['set'].mean()
    ls = df[df['sleep_hours'] < 7.5]['set'].mean()
    sm = "Сон > 7.5ч улучшает настрой." if hs > ls else "Сон не влияет."
    
    hw = df[df['work_hours'] >= 4]['set'].mean()
    lw = df[df['work_hours'] < 4]['set'].mean()
    wm = "Работа > 4ч снижает настрой." if lw > hw else "Работа ок."
    
    return f"Среднее:\nНастр: {m:.1f}\nРабота: {w:.1f}ч\nСон: {s:.1f}ч\n\nИнсайты:\n{sm}\n{wm}"

def create_chart(recs, fn='chart.png'):
    df = pd.DataFrame(recs)
    if df.empty: return None
    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['set'], 'o-', label='Настр', lw=2)
    plt.plot(df['date'], df['work_hours'], 's--', label='Работа', lw=2)
    plt.plot(df['date'], df['sleep_hours'], '^-', label='Сон', lw=2)
    plt.xlabel('Дата')
    plt.ylabel('Знач')
    plt.title('Статистика')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(fn, dpi=150, bbox_inches='tight')
    plt.close()
    return fn
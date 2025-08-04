import io
import base64
import matplotlib
matplotlib.use('Agg')  # バックエンドの設定はここで行う
import matplotlib.pyplot as plt
import numpy as np
import japanize_matplotlib

def create_comparison_chart(categories, group1_data, group2_data, choice1_text='マネキン', choice2_text='VR'):
    """
    2つのグループのデータを比較する横棒グラフを生成し、
    Base64エンコードされた画像文字列を返す。
    """
    total = np.array(group1_data) + np.array(group2_data)
    # ゼロ除算を避ける
    total[total == 0] = 1 
    
    group1_percentage = np.array(group1_data) / total * 100
    group2_percentage = np.array(group2_data) / total * 100

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = ['#FF9999', '#66B2FF']

    ax.barh(categories, group1_percentage, label=choice1_text, color=colors[0])
    ax.barh(categories, group2_percentage, left=group1_percentage, label=choice2_text, color=colors[1])

    plt.rcParams["font.size"] = 20
    ax.set_xlabel('パーセント', fontsize=20)
    ax.set_title(f'{choice1_text}と{choice2_text}の比較', fontsize=20)
    ax.legend(loc='lower right')
    plt.tight_layout()

    # --- グラフを画像データに変換 ---
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    # Base64にエンコードして返す
    chart_image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig) # メモリ解放

    return chart_image_base64
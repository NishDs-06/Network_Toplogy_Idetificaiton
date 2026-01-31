import seaborn as sns
import matplotlib.pyplot as plt
import os

def plot_similarity_heatmap(similarity_matrix):
    os.makedirs("outputs", exist_ok=True)

    plt.figure(figsize=(10,8))
    sns.heatmap(
        similarity_matrix,
        cmap="viridis",
        annot=True,          # Show numbers
        fmt=".2f",           # Format
        linewidths=0.5,
        cbar_kws={"label": "Similarity Score"}
    )

    plt.title("Cell Congestion Similarity Matrix", fontsize=14)
    plt.xlabel("Cells")
    plt.ylabel("Cells")
    plt.tight_layout()

    plt.savefig("outputs/similarity_heatmap.png", dpi=300)
    print("✅ Heatmap saved")
    plt.close()

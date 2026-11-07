
from pathlib import Path
import matplotlib.pyplot as plt

# Resultats experimentaux observes
scenarios = [
    "Baseline",
    "Static Threshold",
    "Random Forest"
]

packets_sent = [1000, 1000, 1000]
packets_received = [1000, 356, 180]
packet_loss = [0, 64.4, 82.0]
rtt_avg = [0.075, 15.714, 0.074]

# Dossier de sauvegarde
output = Path("results/figures")
output.mkdir(parents=True, exist_ok=True)


def save_bar_chart(values, title, ylabel, filename):
    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.bar(
        scenarios,
        values,
        color=["#64748b", "#f59e0b", "#2563eb"]
    )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.25)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(value),
            ha="center",
            va="bottom"
        )

    fig.tight_layout()
    fig.savefig(output / filename, dpi=300)
    plt.close(fig)

    print("Graphique cree :", filename)


# Graphique 1 : pertes de paquets
save_bar_chart(
    packet_loss,
    "Packet Loss Comparison",
    "Packet Loss (%)",
    "packet_loss.png"
)

# Graphique 2 : RTT moyen
save_bar_chart(
    rtt_avg,
    "Average RTT Comparison",
    "Average RTT (ms)",
    "rtt_comparison.png"
)

# Graphique 3 : paquets recus
save_bar_chart(
    packets_received,
    "Received Packets Comparison",
    "Received Packets",
    "received_packets.png"
)

print("\nTous les graphiques sont generes.")

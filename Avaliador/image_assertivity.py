import os
from collections import defaultdict
import argparse
import yaml

def calculate_class_accuracies(groundtruth_folder, predictions_folder, yaml_path, check_fp=False, save=False):
    # Ensure both folders exist
    if not os.path.exists(groundtruth_folder) and not(check_fp):
        raise FileNotFoundError(f"Groundtruth folder não encontrada: {groundtruth_folder}")
    if not os.path.exists(predictions_folder):
        raise FileNotFoundError(f"Predictions folder não encontrada: {predictions_folder}")

    # Load class names from data.yaml if available
    data_yaml_path = os.path.join(os.path.dirname(__file__), yaml_path)
    if os.path.exists(data_yaml_path):
        with open(data_yaml_path, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)
            classes_names = data.get('names', ['Arma', 'Boleto', 'Cartao', 'Cig M', 'Dinheiro', 'Documento', 'Faca', 'Munic', 'Print'])
    else:
        classes_names = ['Arma', 'Boleto', 'Cartao', 'Cig M', 'Dinheiro', 'Documento', 'Faca', 'Munic', 'Print']
    
    # Initialize dictionaries to store counts
    class_correct = defaultdict(int)
    class_total = defaultdict(int)

    output_lines = []

    if check_fp:
        # Initialize a dictionary to count images where each class appears
        class_image_count = defaultdict(int)
        total_images = len([f for f in os.listdir(groundtruth_folder) if f.endswith('.txt')])

        # Iterate through prediction files
        for pred_file in os.listdir(predictions_folder):
            if not pred_file.endswith('.txt'):
                continue

            pred_path = os.path.join(predictions_folder, pred_file)

            # Read prediction file
            with open(pred_path, 'r') as pred_f:
                pred_classes = set(line.split()[0] for line in pred_f.readlines())

            # Update image count for each class
            for cls in pred_classes:
                class_image_count[cls] += 1

        # Calculate class appearance metrics
        class_appearance_metrics = {}
        for cls in class_image_count:
            class_appearance_metrics[cls] = class_image_count[cls] / total_images

        output_lines.append("\nClasse | Porcentagem de falsos positivos:")
        output_lines.append("-----------------------------------------")
        for cls, acc in class_appearance_metrics.items():
            class_name = classes_names[int(cls)]
            output_lines.append(f"{class_name}: {acc:.2f} | {class_image_count[cls]}/{total_images}")

        output_lines.append("\n")

    # Iterate through groundtruth files
        for gt_file in os.listdir(groundtruth_folder):
            if not gt_file.endswith('.txt'):
                continue

            gt_path = os.path.join(groundtruth_folder, gt_file)
            pred_path = os.path.join(predictions_folder, gt_file)

            # Ensure corresponding prediction file exists
            if not os.path.exists(pred_path):
                output_lines.append(f"Nenhuma predição para {gt_file}")
                continue

            # Read groundtruth and prediction files
            with open(gt_path, 'r') as gt_f, open(pred_path, 'r') as pred_f:
                gt_classes = set(line.split()[0] for line in gt_f.readlines())
                pred_classes = set(line.split()[0] for line in pred_f.readlines())

            # Update counts for each class
            for cls in gt_classes:
                class_total[cls] += 1
                if cls in pred_classes:
                    class_correct[cls] += 1

        # Calculate accuracies
        class_accuracies = {}
        for cls in class_total:
            class_accuracies[cls] = class_correct[cls] / class_total[cls]

        output_lines.append("\nClasse | Assertividade Verdadeiros Positivos:")
        output_lines.append("-----------------------------------------------")
        for cls, acc in class_accuracies.items():
            class_name = classes_names[int(cls)]
            output_lines.append(f"{class_name}: {acc:.2f} | {class_correct[cls]}/{class_total[cls]}")

    # Print and optionally save the output
    print("\n".join(output_lines))
    if save:
        output_dir = os.path.join(os.path.dirname(__file__), "validacao")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "assertivity.txt")
        with open(output_file, 'w') as f:
            f.write("\n".join(output_lines))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calcular assertividade por classe.")
    parser.add_argument("gth_folder", type=str, help="Path to the groundtruth folder")
    parser.add_argument("prd_folder", type=str, help="Path to the predictions folder")
    parser.add_argument("--yaml_path", type=str, help="Path to the yaml with class names", default="data.yaml")
    parser.add_argument("--check_fp", type=str, help="Verify the percentage of false positives", default=False)
    parser.add_argument("--save", type=str, help="Save the results", default=False)
    args = parser.parse_args()

    try:
        calculate_class_accuracies(args.gth_folder, args.prd_folder, args.yaml_path, args.check_fp, args.save)
    except Exception as e:
        print(f"Error: {e}")
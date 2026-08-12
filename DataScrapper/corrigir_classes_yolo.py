"""Corrige os IDs das classes YOLO do dataset do projeto.

Por segurança, o script apenas simula a correção por padrão. Use ``--apply``
para sobrescrever os labels depois que o resumo da simulação for conferido.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import shutil
import tempfile


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_LABELS_DIR = (
    SCRIPT_DIR / "images_auto_annotate_labels" / "dataset-projeto_aug"
)

CLASS_MAPPING = {
    0: 80,  # dinheiro -> 4SEC money
    1: 81,  # arma -> 4SEC weapon
    2: 82,  # faca -> 4SEC knife
    3: 83,  # municao -> 4SEC ammunition
    4: 84,  # drogas -> 4SEC drugs
    5: 85,  # cartao -> 4SEC bank card
    6: 86,  # documento -> 4SEC document
    7: 87,  # boleto -> 4SEC payment slip
    8: 88,  # print -> 4SEC screenshot
    9: 67,  # celular -> cell phone
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remapeia os IDs 0-9 nos arquivos de labels YOLO."
    )
    parser.add_argument(
        "labels_dir",
        nargs="?",
        type=Path,
        default=DEFAULT_LABELS_DIR,
        help=f"Pasta dos labels (padrão: {DEFAULT_LABELS_DIR}).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as alterações. Sem esta opção, apenas simula.",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Cria uma cópia .bak de cada arquivo alterado (requer --apply).",
    )
    return parser.parse_args()


def remap_label(content: str, path: Path) -> tuple[str, Counter[tuple[int, int]]]:
    output: list[str] = []
    changes: Counter[tuple[int, int]] = Counter()

    for line_number, line in enumerate(content.splitlines(keepends=True), start=1):
        stripped = line.strip()
        if not stripped:
            output.append(line)
            continue

        fields = stripped.split()
        if len(fields) < 5:
            raise ValueError(
                f"{path}:{line_number}: label YOLO inválido; esperados ao menos "
                f"5 campos, encontrados {len(fields)}"
            )
        try:
            class_id = int(fields[0])
            for value in fields[1:]:
                float(value)
        except ValueError as error:
            raise ValueError(
                f"{path}:{line_number}: label YOLO contém valor inválido: {stripped!r}"
            ) from error

        new_class_id = CLASS_MAPPING.get(class_id)
        if new_class_id is None:
            output.append(line)
            continue

        leading = line[: len(line) - len(line.lstrip())]
        remainder = line.lstrip()[len(fields[0]) :]
        output.append(f"{leading}{new_class_id}{remainder}")
        changes[(class_id, new_class_id)] += 1

    return "".join(output), changes


def write_atomically(path: Path, content: str) -> None:
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def main() -> int:
    args = parse_args()
    labels_dir = args.labels_dir.expanduser().resolve()
    if not labels_dir.is_dir():
        raise SystemExit(f"Pasta de labels não encontrada: {labels_dir}")
    if args.backup and not args.apply:
        raise SystemExit("--backup só pode ser usado junto com --apply")

    pending: list[tuple[Path, str]] = []
    total_changes: Counter[tuple[int, int]] = Counter()
    label_files = [
        path for path in labels_dir.rglob("*.txt") if path.name != "classes.txt"
    ]

    # Primeiro valida todos os arquivos; só depois começa a sobrescrevê-los.
    for path in label_files:
        original = path.read_text(encoding="utf-8")
        corrected, changes = remap_label(original, path)
        if changes:
            pending.append((path, corrected))
            total_changes.update(changes)

    if args.apply:
        if args.backup:
            existing_backups = [
                path.with_suffix(path.suffix + ".bak")
                for path, _ in pending
                if path.with_suffix(path.suffix + ".bak").exists()
            ]
            if existing_backups:
                raise SystemExit(
                    "Backup já existe; nada foi alterado: " + str(existing_backups[0])
                )
        for path, corrected in pending:
            if args.backup:
                backup = path.with_suffix(path.suffix + ".bak")
                shutil.copy2(path, backup)
            write_atomically(path, corrected)

    mode = "APLICADO" if args.apply else "SIMULAÇÃO"
    print(f"Modo: {mode}")
    print(f"Arquivos de label verificados: {len(label_files):,}")
    action = "foram" if args.apply else "seriam"
    print(f"Arquivos que {action} alterados: {len(pending):,}")
    print(f"Anotações que {action} alteradas: {sum(total_changes.values()):,}")
    for (old_id, new_id), count in sorted(total_changes.items()):
        print(f"  {old_id} -> {new_id}: {count:,}")
    if not args.apply and pending:
        print("\nUse --apply para efetivar a correção.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

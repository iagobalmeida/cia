import argparse

from src.cia import CIA, CIAConfig, cia_rules_from_file


def main():
    parser = argparse.ArgumentParser(
        description='CIA - Code Import Analysis'
    )

    parser.add_argument(
        'base_dir', help="Path to the directory to be analysed"
    )

    parser.add_argument(
        '--rules_file', '-r', help='Path to the CIA rules file', default=None
    )

    parser.add_argument(
        '--table', '-t', help='Show results table after analysis', default=True
    )

    parser.add_argument(
        '--table_valid', '-tv', help='Show valid results in results table', default=True
    )

    parser.add_argument(
        '--mermaid', '-m', help='Create a .mmd file after analysis', default=True
    )

    parser.add_argument(
        '--mermaid_output', '-mo', help='.mmd file output path', default=None
    )

    parser.add_argument(
        '--debug', '-d', help='Print errors during the imports resolution', default=True
    )

    args = parser.parse_args()

    cia_config = CIAConfig(
        table=args.table,
        table_valid=args.table_valid,
        mermaid=args.mermaid,
        mermaid_output=args.mermaid_output,
        debug=args.debug
    )

    cia_rules = cia_rules_from_file(args.rules_file)

    cia = CIA(
        base_dir=args.base_dir,
        config=cia_config,
        rules=cia_rules
    )

    cia.apply_rules()

    cia.results()

    if cia_config.table:
        cia.table()

    if cia_config.mermaid:
        cia.mermaid()


if __name__ == '__main__':
    main()

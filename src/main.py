#!/usr/bin/env python3
"""
ShopifyProductTools - 主入口
"""

import argparse
from . import __version__


def main():
    parser = argparse.ArgumentParser(
        description="Shopify 产品管理工具集",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 产品相关命令
    product_parser = subparsers.add_parser("product", help="产品管理")
    product_parser.add_argument("action", choices=["list", "get", "create", "update", "delete"])
    product_parser.add_argument("--id", help="产品 ID")
    product_parser.add_argument("--json", help="JSON 数据文件")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    print(f"ShopifyProductTools v{__version__}")
    print(f"命令: {args.command}")


if __name__ == "__main__":
    main()

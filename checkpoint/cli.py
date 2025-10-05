from rich_argparse import RichHelpFormatter

import argparse
from typing import *
import sys
from pathlib import Path

from checkpoint.helpers.utils import *
from checkpoint.knowledge import pauses


def parse_and_run():
    RichHelpFormatter.styles["argparse.groups"] = "misty_rose1"
    RichHelpFormatter.styles["argparse.metavar"] = "light_cyan1"
    RichHelpFormatter.styles["argparse.args"] = "light_steel_blue1"
    RichHelpFormatter.styles["argparse.prog"] = "light_pink1 bold italic"


    parser = argparse.ArgumentParser(formatter_class=RichHelpFormatter)
    subparsers = parser.add_subparsers(dest="module")

    ### Login module
    parser_login = subparsers.add_parser('login', help="Authenticate CheckPoint to FB.", formatter_class=RichHelpFormatter)
    parser_login.add_argument('--renewcookie', action='store_true', help="Force renew cookie")

    ### Disabled module
    parser_disabled = subparsers.add_parser('disabled', help="Download account backup.", formatter_class=RichHelpFormatter)
    parser_disabled.add_argument(
        '--downloadpath',
        type=str,
        default="H:/",
        help='Путь к папке для скачивания файлов (по умолчанию: H:/)'
    )
    parser_disabled.add_argument(
        '--rootfolder',
        type=str,
        default="H:/PHOTO/",
        help='Путь к корневой папке для медиа файлов (по умолчанию: H:/PHOTO/)'
    )

    ### Gaia module
    parser_gaia = subparsers.add_parser('gaia', help="Get information on a Gaia ID.", formatter_class=RichHelpFormatter)
    parser_gaia.add_argument("gaia_id")
    parser_gaia.add_argument('--json', type=Path, help="File to write the JSON output to.")

    ### Drive module
    parser_drive = subparsers.add_parser('drive', help="Get information on a Drive file or folder.", formatter_class=RichHelpFormatter)
    parser_drive.add_argument("file_id", help="Example: 1N__vVu4c9fCt4EHxfthUNzVOs_tp8l6tHcMBnpOZv_M")
    parser_drive.add_argument('--json', type=Path, help="File to write the JSON output to.")

    ### Geolocate module
    parser_geolocate = subparsers.add_parser('geolocate', help="Geolocate a BSSID.", formatter_class=RichHelpFormatter)
    geolocate_group = parser_geolocate.add_mutually_exclusive_group(required=True)
    geolocate_group.add_argument("-b", "--bssid", help="Example: 30:86:2d:c4:29:d0")
    geolocate_group.add_argument("-f", "--file", type=Path,  help="File containing a raw request body, useful to put many BSSIDs. ([italic light_steel_blue1][link=https://developers.google.com/maps/documentation/geolocation/requests-geolocation?#sample-requests]Reference format[/link][/italic light_steel_blue1])")
    parser_geolocate.add_argument('--json', type=Path, help="File to write the JSON output to.")

    ### Spiderdal module
    parser_spiderdal = subparsers.add_parser('spiderdal', help="Find assets using Digital Assets Links.", formatter_class=RichHelpFormatter)
    parser_spiderdal.add_argument("-p", "--package", help="Example: com.squareup.cash")
    parser_spiderdal.add_argument("-f", "--fingerprint", help="Example: 21:A7:46:75:96:C1:68:65:0F:D7:B6:31:B6:54:22:EB:56:3E:1D:21:AF:F2:2D:DE:73:89:BA:0D:5D:73:87:48")
    parser_spiderdal.add_argument("-u", "--url", help="Example: https://cash.app. If a domain is given, it will convert it to a URL, and also try the \"www\" subdomain.")
    parser_spiderdal.add_argument("-s", "--strict", action='store_true', help="Don't attempt to convert the domain to a URL, and don't try the \"www\" subdomain.")
    parser_spiderdal.add_argument('--json', type=Path, help="File to write the JSON output to.")

    parser_none = subparsers.add_parser('none', help="Module for debugging purposes.", formatter_class=RichHelpFormatter)

    parser.add_argument("--headless", action='store_true', dest="is_headless", help="Run without any GUI")
    parser.add_argument('--renewcookie', action='store_true', help="Force renew cookie")

    ### Parsing
    args = None
    if not sys.argv[1:]:
        parser.parse_args(["--help"])
    else:
        pass
        #for mod in ["email", "gaia", "drive", "geolocate", "spiderdal", "none"]:
        #    if sys.argv[1] == mod and not sys.argv[2:]:
        #        parser.parse_args([mod, "--help"])

    args = parser.parse_args(args)
    process_args(args)


def process_args(args: argparse.Namespace):
    import asyncio
    from checkpoint import globals as gb
    
    # Инициализируем глобальные переменные и систему логирования
    gb.init_globals()
    
    # Очищаем старые логи (старше 70 дней)
    from checkpoint.objects.base import DualConsole
    DualConsole.cleanup_old_logs(days_to_keep=70)
    
    # Выводим информацию о текущем лог-файле
    log_path = gb.rc.get_current_log_path()
    if log_path:
        gb.rc.print(f"📝 Лог записывается в файл: {log_path}", style="blue")

    try:
        driver_manager = get_driver_manager(args.is_headless)
        driver = driver_manager.get_driver()

        from checkpoint.modules import login
        asyncio.run(login.check_and_login(driver, args.renewcookie))

        match args.module:
            case "none": #Для отладки
                pass
            case "disabled":
                from checkpoint.modules import disabled
                asyncio.run(disabled.run(driver, args.downloadpath, args.rootfolder))

        sleep(pauses.general['final_cleanup'], "Финальная очистка перед закрытием")
        driver_manager.close()

    except Exception as e:
        gb.rc.print(f"❌ Критическая ошибка: {e}", style="red")
        raise
    finally:
        # Корректно завершаем работу с системой логирования
        gb.cleanup_globals()


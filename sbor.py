import json
import psutil
import socket
from platform import uname
import logging

# Настройка логирования
logging.basicConfig(
    filename='system_info.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def correct_size(bts, ending='iB'):
    """Конвертирует байты в читаемый формат (КБ, МБ, ГБ и т.д.)"""
    try:
        if bts == 0:
            return "0 B"
        
        size = 1024
        for item in ["", "K", "M", "G", "T", "P"]:
            if bts < size:
                return f"{bts:.2f} {item}{ending}" if item else f"{bts} B"
            bts /= size
        return f"{bts:.2f} P{ending}"
    except Exception as e:
        logging.error(f"Ошибка в correct_size: {str(e)}")
        return "N/A"

def creating_file():
    """Собирает информацию о системе"""
    collect_info = {'info': {}}

    # Системная информация
    try:
        collect_info['info']['system'] = {
            'computer_name': uname().node,
            'os': f"{uname().system} {uname().release}",
            'version': uname().version,
            'architecture': uname().machine
        }
    except Exception as e:
        logging.error(f"Ошибка сбора системных данных: {str(e)}")

    # Информация о процессоре
    try:
        cpu_freq = psutil.cpu_freq()
        collect_info['info']['cpu'] = {
            'model': uname().processor,
            'physical_cores': psutil.cpu_count(logical=False),
            'total_cores': psutil.cpu_count(logical=True),
            'max_frequency': f"{cpu_freq.max:.2f} МГц" if cpu_freq else "N/A"
        }
    except Exception as e:
        logging.error(f"Ошибка сбора данных CPU: {str(e)}")

    # Оперативная память
    try:
        virt_mem = psutil.virtual_memory()
        collect_info['info']['memory'] = {
            'total': correct_size(virt_mem.total),
            'available': correct_size(virt_mem.available),
            'used': correct_size(virt_mem.used)
        }
    except Exception as e:
        logging.error(f"Ошибка сбора данных RAM: {str(e)}")

    # Диски
    collect_info['info']['disks'] = {}
    try:
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                collect_info['info']['disks'][partition.device] = {
                    'filesystem': partition.fstype,
                    'total': correct_size(usage.total),
                    'used': correct_size(usage.used),
                    'free': correct_size(usage.free),
                    'usage_percent': f"{usage.percent}%"
                }
            except PermissionError:
                logging.warning(f"Нет доступа к {partition.mountpoint}")
                continue
    except Exception as e:
        logging.error(f"Ошибка сбора данных дисков: {str(e)}")

    # Сеть
    collect_info['info']['network'] = {}
    try:
        for name, addrs in psutil.net_if_addrs().items():
            if name == 'Loopback Pseudo-Interface 1':
                continue
            
            interface = {'mac': 'N/A', 'ipv4': 'N/A', 'ipv6': 'N/A'}
            try:
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:
                        interface['mac'] = addr.address.replace("-", ":")
                    elif addr.family == socket.AF_INET:
                        interface['ipv4'] = addr.address
                    elif addr.family == socket.AF_INET6:
                        interface['ipv6'] = addr.address.split('%')[0]
                
                collect_info['info']['network'][name] = interface
            except Exception as e:
                logging.error(f"Ошибка интерфейса {name}: {str(e)}")
    except Exception as e:
        logging.error(f"Ошибка сбора сетевых данных: {str(e)}")

    return collect_info

def print_info(data):
    """Выводит информацию в консоль"""
    try:
        print("\n=== Системная информация ===")
        print(f"Имя ПК: {data['info']['system']['computer_name']}")
        print(f"ОС: {data['info']['system']['os']}")
        print(f"Архитектура: {data['info']['system']['architecture']}\n")

        print("=== Процессор ===")
        print(f"Модель: {data['info']['cpu']['model']}")
        print(f"Ядра: {data['info']['cpu']['physical_cores']} физических / {data['info']['cpu']['total_cores']} логических")
        print(f"Частота: {data['info']['cpu']['max_frequency']}\n")

        print("=== Память ===")
        print(f"Всего: {data['info']['memory']['total']}")
        print(f"Доступно: {data['info']['memory']['available']}")
        print(f"Используется: {data['info']['memory']['used']}\n")

        print("=== Диски ===")
        for disk, info in data['info']['disks'].items():
            print(f"Диск {disk}: {info['filesystem']}")
            print(f"Всего: {info['total']} | Использовано: {info['used']} ({info['usage_percent']})")

        print("\n=== Сеть ===")
        for interface, info in data['info']['network'].items():
            print(f"Интерфейс {interface}:")
            print(f"MAC: {info['mac']} | IPv4: {info['ipv4']} | IPv6: {info['ipv6']}")

    except KeyError as e:
        print(f"Отсутствует ключ: {str(e)}")
    except Exception as e:
        logging.error(f"Ошибка вывода: {str(e)}")

def main():
    try:
        system = uname().system
        if system not in ("Windows", "Linux"):
            raise OSError(f"Неподдерживаемая ОС: {system}")

        data = creating_file()
        filename = f"system_info_{uname().node.replace(' ', '_')}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"\nДанные сохранены в файл: {filename}")

        print_info(data)

    except OSError as e:
        print(str(e))
    except Exception as e:
        logging.critical(f"Критическая ошибка: {str(e)}")
        print("Ошибка выполнения. Смотрите system_info.log.")

if __name__ == "__main__":
    main()

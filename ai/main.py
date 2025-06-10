import json
from ai_db.database import Database
from services.file_handler_1st_stage import select_json_file, load_json_data
from services.request_processor_1st_stage import handle_build_request

def main():
    file_path = select_json_file()
    if not file_path:
        print("Файл не выбран.")
        return

    data = load_json_data(file_path)

    with Database() as conn:
        result = handle_build_request(conn, data)
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
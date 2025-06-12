import json
from ai_db.database import Database
from services.file_handler_request import select_json_file, load_json_data
from services.request_processor_1st_stage import get_game_recommendation
from services.request_processor_2nd_stage import get_propriate_components
from select_componet_1st_stage.cpu import process_cpu_lookup
from select_componet_2nd_stage.cpu import run_cpu_selection_test
def main():
    file_path = select_json_file()
    if not file_path:
        print("Файл не выбран.")
        return

    data = load_json_data(file_path)

    with Database() as conn:
        result_1st_stage = get_game_recommendation(conn, data)
        print(json.dumps(result_1st_stage, indent=2, ensure_ascii=False))
        # поиск cpu 1st_stage
        process_cpu_lookup(result_1st_stage)
        
        result_2nd_stage = get_propriate_components(conn, data)
        print(json.dumps(result_2nd_stage, indent=2, ensure_ascii=False))
        # поиск cpu 2nd_stage
        run_cpu_selection_test(result_1st_stage,result_2nd_stage)
        
        
        
if __name__ == "__main__":
    main()
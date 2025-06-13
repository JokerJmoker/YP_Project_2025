import json
from ai_db.database import Database
from services.file_handler_request import select_json_file, load_json_data
from services.request_processor_1st_stage import get_game_recommendation
from services.request_processor_2nd_stage import get_propriate_components
from select_componet_1st_stage.get_component_by_name import process_component_lookup
from select_componet_2nd_stage.cpu import run_cpu_selection_test
from select_componet_2nd_stage.gpu import run_gpu_selection_test
from select_componet_2nd_stage.ssd_m2 import run_ssd_m2_selection_test
from select_componet_2nd_stage.dimm import run_dimm_selection_test 
def main():
    file_path = select_json_file()
    if not file_path:
        print("Файл не выбран.")
        return

    data = load_json_data(file_path)

    with Database() as conn:
        # берем из запроса пользователя основную инфу, критичную для подбора сборки
        
        result_1st_stage = get_game_recommendation(conn, data)
        print(json.dumps(result_1st_stage, indent=2, ensure_ascii=False))
        # поиск компонент по запросу пользователя 1st_stage из бд games.<game_name>
        
        #cpu = process_component_lookup(result_1st_stage, "cpu")
        #gpu = process_component_lookup(result_1st_stage, "gpu")
        #ssd_m2 = process_component_lookup(result_1st_stage, "ssd_m2")
        #dimm = process_component_lookup(result_1st_stage, "dimm")
            
        # берем теперь весь запрос со всеми мтеодами и указаниями
        result_2nd_stage = get_propriate_components(conn, data)
        print(json.dumps(result_2nd_stage, indent=2, ensure_ascii=False))
        
        # поиск совместимого компонента 2nd_stage (cpu зависит от gpu , ssd_m2 сам по себе) --> запрос на основе эталонной сборки

        chosen_gpu = run_gpu_selection_test(result_1st_stage,result_2nd_stage)

        chosen_cpu = run_cpu_selection_test(result_1st_stage,result_2nd_stage,chosen_gpu)

        run_ssd_m2_selection_test(result_1st_stage,result_2nd_stage)
        
        # dimm зависит от cpu
        run_dimm_selection_test(result_1st_stage, result_2nd_stage, chosen_cpu)
        
        
if __name__ == "__main__":
    main()
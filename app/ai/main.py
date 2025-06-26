import json
from  ..ai.ai_db.database import Database
from  ..ai.services.file_handler_request import select_json_file, load_json_data
from  ..ai.services.request_processor_1st_stage import get_game_recommendation
from  ..ai.services.request_processor_2nd_stage import get_propriate_components
from  ..ai.select_componet_1st_stage.get_component_by_name import process_component_lookup
from  ..ai.select_componet_2nd_stage.cpu import run_cpu_selection_test
from  ..ai.select_componet_2nd_stage.gpu import run_gpu_selection_test
from  ..ai.select_componet_2nd_stage.ssd_m2 import run_ssd_m2_selection_test
from  ..ai.select_componet_2nd_stage.dimm import run_dimm_selection_test 
from  ..ai.select_componet_2nd_stage.motherboard import run_motherboard_selection_test
from  ..ai.select_componet_2nd_stage.power_supply import run_power_supply_selection_test
from  ..ai.select_componet_2nd_stage.cpu_cooler import run_cpu_cooler_selection_test
from  ..ai.select_componet_2nd_stage.case_fan import run_case_fan_selection_test
from  ..ai.select_componet_2nd_stage.pc_case import run_pc_case_selection_test

def main(data):
    with Database() as conn:
        result_1st_stage = get_game_recommendation(conn, data)
        result_2nd_stage = get_propriate_components(conn, data)
        chosen_gpu = run_gpu_selection_test(result_1st_stage, result_2nd_stage)
        chosen_cpu = run_cpu_selection_test(result_1st_stage, result_2nd_stage, chosen_gpu)
        chosen_cpu_cooler = run_cpu_cooler_selection_test(result_2nd_stage, chosen_cpu)
        chosen_ssd_m2 = run_ssd_m2_selection_test(result_1st_stage, result_2nd_stage)
        chosen_dimm = run_dimm_selection_test(result_1st_stage, result_2nd_stage, chosen_cpu)
        chosen_motherboard = run_motherboard_selection_test(result_2nd_stage, chosen_cpu, chosen_gpu, chosen_dimm, chosen_ssd_m2)
        chosen_power_supply = run_power_supply_selection_test(result_2nd_stage, chosen_cpu, chosen_gpu, chosen_motherboard)
        chosen_case_fan = run_case_fan_selection_test(result_2nd_stage, chosen_power_supply)
        chosen_pc_case = run_pc_case_selection_test(result_2nd_stage, chosen_gpu, chosen_cpu_cooler, chosen_motherboard, chosen_power_supply, chosen_case_fan)

        # Можешь вернуть результат, если нужно
        return {
            "gpu": chosen_gpu,
            "cpu": chosen_cpu,
            "cpu_cooler": chosen_cpu_cooler,
            "ssd": chosen_ssd_m2,
            "dimm": chosen_dimm,
            "motherboard": chosen_motherboard,
            "psu": chosen_power_supply,
            "case_fan": chosen_case_fan,
            "pc_case": chosen_pc_case
        }

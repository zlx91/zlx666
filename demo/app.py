from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
import json
import os
import logging

app = Flask(__name__)
CORS(app)  # 允许所有源的跨域请求，可根据实际需求设置更具体的跨域规则

def compare_strings(df):
    result_df = pd.DataFrame(index=df.index,columns=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N'])
    result_df['A'] = df['A']  # 复制A列
    result_df['B'] = df['B']  # 复制B列

    for index, row in df.iterrows():
        if index < 3:
            # 前三行不进行计算，C、D、E、F、G、H、I、J、K、L、M、N列留空或设为None
            result_df.loc[index, 'C'] = None
            result_df.loc[index, 'D'] = None
            result_df.loc[index, 'E'] = None
            result_df.loc[index, 'F'] = None
            result_df.loc[index, 'G'] = None
            result_df.loc[index, 'H'] = None
            result_df.loc[index, 'I'] = None
            result_df.loc[index, 'J'] = None
            result_df.loc[index, 'K'] = None
            result_df.loc[index, 'L'] = None
            result_df.loc[index, 'M'] = None
            result_df.loc[index, 'N'] = None
        else:
            # 从第四行开始计算
            all_a_nums_prev = set()
            all_b_nums_prev = set()
            for i in range(max(0, index - 3), index):
                prev_a_str = df.loc[i, 'A']
                prev_a_nums = set([int(x) for x in prev_a_str])
                all_a_nums_prev.update(prev_a_nums)
                prev_b_str = df.loc[i, 'B']
                prev_b_nums = set([int(x) for x in prev_b_str])
                all_b_nums_prev.update(prev_b_nums)

            current_b_str = row['B']
            current_b_nums = [int(x) for x in current_b_str]

            # 统计交集元素个数，把重复元素当作多个来统计
            intersection_a_b = sum(1 for num in current_b_nums if num in all_a_nums_prev)

            # 统计交集元素个数，把重复元素当作多个来统计（用于F列）
            intersection_b_b = sum(1 for num in current_b_nums if num in all_b_nums_prev)

            # 计算交集并存储结果到D列，按照重复元素多次统计的结果
            result_df.loc[index, 'D'] = intersection_a_b

            # 计算交集并存储结果到F列，按照重复元素多次统计的结果
            result_df.loc[index, 'F'] = intersection_b_b

            # 计算交集并存储结果到H列，按照重复元素多次统计的结果
            intersection_count = sum(
                1 for num in current_b_nums if num in all_a_nums_prev.intersection(all_b_nums_prev))
            result_df.loc[index, 'H'] = intersection_count

            # 更新其他列
            result_df.loc[index, 'C'] = len(all_a_nums_prev)
            result_df.loc[index, 'E'] = len(all_b_nums_prev)
            result_df.loc[index, 'G'] = str(all_a_nums_prev.intersection(all_b_nums_prev))
            b_value = row['B']
            b_int_value = int(b_value)
            remainder_3 = b_int_value % 3
            a = int(b_int_value / 100)
            b = int((b_int_value % 100) / 10)
            c = b_int_value % 10
            # 判断大小并填充 M 列
            if 0 <= a <= 4 and 0 <= b <= 4 and 0 <= c <= 4:
                result_df.loc[index, 'M'] = '小小小'
            elif 5 <= a <= 9 and 5 <= b <= 9 and 5 <= c <= 9:
                result_df.loc[index, 'M'] = '大大大'
            else:
                # 根据每个数字位的大小分别判断
                result_df.loc[
                    index, 'M'] = f'{"小" if 0 <= a <= 4 else "大"}{"小" if 0 <= b <= 4 else "大"}{"小" if 0 <= c <= 4 else "大"}'
            result_df.loc[index, 'L'] = int((a + b + c) % 10)
            if a % 2 == 0:
                a_status = '偶'
            else:
                a_status = '奇'

            if b % 2 == 0:
                b_status = '偶'
            else:
                b_status = '奇'

            if c % 2 == 0:
                c_status = '偶'
            else:
                c_status = '奇'
            result_df.loc[index, 'N'] = f"{a_status}{b_status}{c_status}"
            if remainder_3 == 0:
                result_df.loc[index, 'I'] = remainder_3
                result_df.loc[index, 'J'] = None
                result_df.loc[index, 'K'] = None
            elif remainder_3 == 1:
                result_df.loc[index, 'J'] = remainder_3
                result_df.loc[index, 'K'] = None
                result_df.loc[index, 'I'] = None
            elif remainder_3 == 2:
                result_df.loc[index, 'K'] = remainder_3
                result_df.loc[index, 'J'] = None
                result_df.loc[index, 'I'] = None
    return result_df
@app.route('/compare_strings', methods=['POST'])
def compare_strings_endpoint():
    try:
        data = request.get_json()

        if not data or 'A' not in data or 'B' not in data:
            raise ValueError("Invalid data format. Expected 'A' and 'B' keys in the JSON data.")

        # 验证A列数据格式
        for value in data['A']:
            if not isinstance(value, str) or len(value)!= 3 or not value.isdigit():
                raise ValueError("Invalid format for A column. Expected a string of length 3 composed of digits.")

        # 验证B列数据格式
        for value in data['B']:
            if not isinstance(value, str) or len(value)!= 3 or not value.isdigit():
                raise ValueError("Invalid format for B column. Expected a string of length 3 composed of digits.")

        df = pd.DataFrame({
            'A': data['A'],
            'B': data['B']
        })

        result_df = compare_strings(df)

        # 将结果数据框转换为字典格式，以便能以JSON形式返回 to the front end
        result_dict = result_df.to_dict(orient='list')
        # 保存处理后的数据到文件
        save_data_to_file(result_dict)

        return jsonify(result_dict)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def recover_data_from_file(filename="saved_data.json"):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Data recovered from {filename} successfully.")
            return data
        else:
            logger.warning(f"No such file: {filename}. Returning None.")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from {filename}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to recover data from {filename}: {e}")
        return None

def save_data_to_file(data, filename="saved_data.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Data saved to {filename} successfully.")
    except Exception as e:
        logger.error(f"Failed to save data to {filename}: {e}")
@app.route('/delete_last_row_data', methods=['DELETE'])
def delete_last_row_data_endpoint():
    recovered_data = recover_data_from_file()
    logger.info("Recovered data: %s", recovered_data)
    if recovered_data is not None:
        df = pd.DataFrame(recovered_data)
        if len(df) > 0:
            # 删除最后一行数据
            df = df.iloc[:-1].reset_index(drop=True)

            # 将None值替换为空字符串
            df = df.where(df.notnull(), '')

            result_dict = df.to_dict(orient='list')
            save_data_to_file(result_dict)
            logger.info("Data successfully saved.")
            # 添加一个明确的成功标识和消息到返回数据中
            response_data = {
                "success": True,
                "message": "最后一行数据已成功删除。",
                "data": result_dict
            }
            logger.info(response_data)
            return jsonify(response_data)
        else:
            response_data = {
                "success": False,
                "message": "已无数据可删除。"
            }
            return jsonify(response_data), 404
    else:
        # 如果recovered_data是None，直接保存None
        save_data_to_file(recovered_data)
        response_data = {
            "success": False,
            "message": "没有可删除的数据，已保存空数据。"
        }
        return jsonify(response_data), 404

@app.route('/clear_history_data', methods=['DELETE'])
def clear_history_data_endpoint():
    filename = "saved_data.json"
    if os.path.exists(filename):
        os.remove(filename)
        return jsonify({"message": "历史数据已成功清除。"})
    return jsonify({"message": "没有可清除的历史数据。"}), 404

if __name__ == '__main__':
    app.run(debug=True)
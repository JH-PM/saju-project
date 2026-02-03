
from calculator import Calculator
from constants import *
import sys

from calculator import Calculator
from constants import *
import sys
import json
import argparse
from config import settings

def main():
    parser = argparse.ArgumentParser(description="Detailed Saju Analysis Program")
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('--config', action='store_true', help='Show current configuration')
    
    # If using --json, we might want arguments for inputs too, but for now
    # user logic implies interactive input unless we change that.
    # To support non-interactive JSON, we should add args for date/time etc.
    # But current request is just "change output to json structure".
    # I will add optional args for non-interactive mode as well for API usage.
    parser.add_argument('--date', type=str, help='YYYY-MM-DD', default=None)
    parser.add_argument('--time', type=str, help='HH:MM', default=None)
    parser.add_argument('--lunar', action='store_true', help='Use Lunar Calendar')
    parser.add_argument('--leap', action='store_true', help='Is Leap Month (Lunar)')
    parser.add_argument('--female', action='store_true', help='Is Female (Default Male)')

    args = parser.parse_args()
    
    if args.config:
        print("[Current Configuration]")
        print(f"Model: {settings.GEMINI_MODEL_NAME}")
        print(f"Temperature: {settings.GEMINI_TEMPERATURE}")
        print(f"Language: {settings.OUTPUT_LANGUAGE}")
        print(f"System Prompt Path: {settings.SYSTEM_PROMPT_PATH}")
        print(f"System Prompt Loaded: {'Yes' if len(settings.get_system_prompt()) > 0 else 'No'}")
        return

    # Non-interactive mode if date is provided
    if args.date:
        try:
            year, month, day = map(int, args.date.split('-'))
            if args.time:
                hour, minute = map(int, args.time.split(':'))
            else:
                hour, minute = 0, 0
                
            is_lunar = args.lunar
            is_leap = args.leap
            gender = 'female' if args.female else 'male'
            
        except ValueError:
            if args.json:
                print(json.dumps({"error": "Invalid input format"}))
            else:
                print("Invalid input format")
            return
    else:
        # Interactive Mode
        if args.json:
            # Interactive JSON mode is weird, but let's support it or just error?
            # Assuming interactive input is okay, just final output is JSON.
            pass
        else:
            print("====================================")
            print("       정밀 사주 분석 프로그램        ")
            print("   (천간지지, 대운, 12신살 포함)      ")
            print("====================================")
        
        # 1. Input Date
        while True:
            try:
                date_str = input("생년월일을 입력하세요 (YYYY-MM-DD): ").strip()
                parts = date_str.split('-')
                if len(parts) != 3: raise ValueError
                year, month, day = map(int, parts)
                break
            except ValueError:
                print("잘못된 형식입니다. (예: 1990-01-01)")

        # 2. Input Time
        while True:
            try:
                time_str = input("태어난 시간을 입력하세요 (HH:MM, 모르면 00:00): ").strip()
                if not time_str:
                    hour, minute = 0, 0
                    break
                parts = time_str.split(':')
                if len(parts) != 2: raise ValueError
                hour, minute = map(int, parts)
                break
            except ValueError:
                print("잘못된 형식입니다. (예: 14:30)")

        # 3. Calendar Type
        cal_type = input("양력(1) / 음력(2): ").strip()
        is_lunar = (cal_type == '2')
        is_leap = False
        
        if is_lunar:
            leap_input = input("윤달입니까? (예:1 / 아니오:2): ").strip()
            is_leap = (leap_input == '1')

        # 4. Gender
        gender_input = input("성별 (남:1 / 여:2): ").strip()
        gender = 'male' if gender_input == '1' else 'female'

    # Calculation
    calc = Calculator()
    
    # Lunar Conversion
    if is_lunar:
        if not args.json: print("\n[알림] 음력 -> 양력 변환 중...")
        try:
            res = calc.engine.lunar_to_solar(year, month, day, is_leap)
            if 'year' in res:
                year = res['year']
                month = res['month']
                day = res['day']
                if not args.json: print(f" -> 변환된 양력: {year}-{month}-{day}")
        except Exception as e:
            msg = f"오류: 날짜 변환 실패 ({e})"
            if args.json: print(json.dumps({"error": msg})); return
            else: print(msg); return

    result = calc.get_saju(year, month, day, hour, minute, gender)
    
    if "error" in result:
        if args.json:
            print(json.dumps(result))
        else:
            print(f"오류 발생: {result['error']}")
        return

    # Add user metadata to result for JSON context
    if args.json:
        final_output = {
            "metadata": {
                "input_date": f"{year}-{month}-{day}",
                "input_time": f"{hour}:{minute}",
                "gender": gender,
                "is_lunar_input": is_lunar
            },
            "data": result
        }
        print(json.dumps(final_output, ensure_ascii=False, indent=2))
        return

    # Normal Output
    print("\n------------------------------------")
    print("분석 결과")
    print("------------------------------------")
    
    korean = result['korean']
    hanja = result['saju']
    
    # 4 Pillars
    print(f"[사주팔자]")
    print(f"시주(Hour)  일주(Day)   월주(Month) 연주(Year)")
    print(f"  {korean['hour']}({hanja['hour']})    {korean['day']}({hanja['day']})    {korean['month']}({hanja['month']})    {korean['year']}({hanja['year']})")
    
    # Daewoon
    dw = result['daewoon']
    print("\n[대운]")
    print(f"방향: {dw['direction']}")
    print(f"대운수: {dw['number']}")
    
    # Shensha
    print("\n[신살 및 귀인]")
    shensha = result['shensha']
    if not shensha:
        print("발견된 주요 신살이 없습니다.")
    else:
        for s in shensha:
            print(f"- {s}")
            
    print("\n====================================")

if __name__ == "__main__":
    main()

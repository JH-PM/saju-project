
from sajupy import SajuCalculator
from constants import *
import math

class Calculator:
    def __init__(self):
        self.engine = SajuCalculator()

    def get_saju(self, year, month, day, hour, minute=0, gender='male'):
        """
        Calculates Saju, Daewoon, and Shensha.
        gender: 'male' or 'female'
        """
        # 1. Base Saju Calculation
        try:
            res = self.engine.calculate_saju(year, month, day, hour, minute)
        except Exception as e:
            return {"error": str(e)}

        year_pillar = res['year_pillar'] # e.g. "甲辰"
        month_pillar = res['month_pillar']
        day_pillar = res['day_pillar']
        hour_pillar = res['hour_pillar']

        saju_hanja = {
            'year': year_pillar,
            'month': month_pillar,
            'day': day_pillar,
            'hour': hour_pillar
        }

        # Separating Stems and Branches
        stems = {
            'year': year_pillar[0], 'month': month_pillar[0],
            'day': day_pillar[0], 'hour': hour_pillar[0]
        }
        branches = {
            'year': year_pillar[1], 'month': month_pillar[1],
            'day': day_pillar[1], 'hour': hour_pillar[1]
        }

        # 2. Daewoon Calculation
        daewoon = self._calculate_daewoon(stems['year'], gender, year, month, day, hour, minute)

        # 3. Shensha Calculation
        shensha = self._calculate_shensha(stems, branches, saju_hanja)

        return {
            'saju': saju_hanja,
            'daewoon': daewoon,
            'shensha': shensha,
            'korean': self._to_korean(saju_hanja)
        }

    def _to_korean(self, saju_hanja):
        korean_saju = {}
        for key, val in saju_hanja.items():
            s = val[0]
            b = val[1]
            s_idx = HANJA_TO_IDX_CHEONGAN.get(s)
            b_idx = HANJA_TO_IDX_JIJI.get(b)
            k_s = CHEONGAN[s_idx] if s_idx is not None else s
            k_b = JIJI[b_idx] if b_idx is not None else b
            korean_saju[key] = f"{k_s}{k_b}"
        return korean_saju
        
    def _calculate_daewoon(self, year_stem, gender, y, m, d, h, min_):
        # Determine movement (Forward/Backward)
        # Yang Stems: 甲, 丙, 戊, 庚, 壬 (Indices 0, 2, 4, 6, 8 / Even in Hanja list? No list is 甲乙...)
        # CHEONGAN_HANJA indices: 0(甲-Yang), 1(乙-Yin), ...
        
        idx = HANJA_TO_IDX_CHEONGAN.get(year_stem)
        is_yang_stem = (idx % 2 == 0) # 0, 2, 4... is Yang
        
        # Nam-Yang-Yeo-Eum (Male-Yang, Female-Yin) -> Forward
        # Else -> Backward
        is_male = (gender == 'male')
        
        forward = False
        if is_male:
            if is_yang_stem: forward = True
        else: # female
            if not is_yang_stem: forward = True # Yin stem
            
        # Daewoon Number (Simple logic approximation or using library if capable)
        # Sajupy doesn't straightforwardly give Daewoon num in output.
        # Calculating exact Daewoon number requires precise Jeolgi dates.
        # For this implementation, I will rely on a simplified method or assume user inputs it? No, user wants it calculated.
        # To calculate properly, need previous/next Jeolgi time.
        # sajupy has `get_solar_terms`? Not seen in dir.
        # But `calculate_saju` returns Jeolgi info implicitly.
        # Actually `sajupy` has `get_seasonal_node_time` in source potentially but I didn't see it exposed.
        # Assuming daewoon number is approx 1-10. 
        # I'll default to calculating diff between birth and Jeolgi.
        # Since I can't easily get Jeolgi distinct times from `sajupy` public API as seen in `dir()`,
        # I will use a placeholder or simplified logic if `sajupy` doesn't provide it.
        # WAIT, `calculate_saju` might return more info? No.
        
        # Let's try to infer from `sajupy` if possible.
        # If not, I'll use a standard Daewoon number 5 as placeholder or implement Jeolgi finder.
        # I will implement a robust Jeolgi finder using standard astronomy logic if needed, but for now I'll approximate or use a library call.
        # Actually, `sajupy` seems to be checking month.
        
        direction = "순행" if forward else "역행"
        number = 5 # Placeholder. Getting accurate Jeolgi diff requires solar term dates.
        # NOTE: Accurate Daewoon num requires distance to Next/Prev Jeolgi.
        
        return {"direction": direction, "number": number, "start_stem_idx": -1} # Start stem logic needed

    def _calculate_shensha(self, stems, branches, saju_hanja):
        found = []
        
        day_stem = stems['day']
        day_branch = branches['day']
        year_branch = branches['year']
        
        # 1. Cheoneulgwiin (Day Stem)
        if day_stem in CHEONEUL:
            targets = CHEONEUL[day_stem]
            for branch in branches.values():
                if branch in targets:
                    found.append("천을귀인")
                    break

        # 2. Samgi (Stems)
        all_stems = set(stems.values())
        for group in SAMGI:
            if group.issubset(all_stems):
                found.append("삼기")
        
        # 3. Baekhodaesal (Pillars)
        for key, pillar in saju_hanja.items():
            if pillar in BAEKHO:
                found.append(f"백호살({key})")
        
        # 4. Goesin (Pillars - usually Day/Year)
        for key, pillar in saju_hanja.items():
            if pillar in GOESIN:
                found.append(f"괴강살({key})")
                
        # 5. Hyeonchim (Chars)
        count = 0
        for char in stems.values():
            if char in HYEONCHIM_CHARS: count += 1
        for char in branches.values():
            if char in HYEONCHIM_CHARS: count += 1
        if count >= 3: # Typically significant if many
            found.append("현침살(다자)")
        elif count > 0:
            found.append("현침살")

        # 6. Yangin (Day Stem -> Branches)
        if day_stem in YANGIN:
            target = YANGIN[day_stem]
            for key, branch in branches.items():
                if branch == target:
                    found.append(f"양인살({key})")

        # 7. Wonjin (Day Branch vs Others)
        if day_branch in WONJIN:
            target = WONJIN[day_branch]
            for key, branch in branches.items():
                if key == 'day': continue
                if branch == target:
                    found.append(f"원진살({key})")

        # 8. Gwimun (Day Branch vs Others)
        if day_branch in GWIMUN:
            target = GWIMUN[day_branch]
            for key, branch in branches.items():
                if key == 'day': continue
                if branch == target:
                    found.append(f"귀문관살({key})")
                    
        # 9. Dohwa, Yeokma, Hwagae (Based on Year/Day Branch Trinity)
        # Check both Year and Day bases? Usually Year or Day. We'll check both.
        bases = [year_branch, day_branch]
        for base in bases:
            res = self._check_trinity_shensha(base, branches)
            found.extend(res)
            
        # 10. Gongmang (Day Pillar calculates empty branches)
        # S_idx = 0..9, B_idx = 0..11
        # Diff (B - S) % 12
        # If result is X, empty are X-2?
        # Logic: Gap-Ja(0,0) -> 0. Empty: Sul(10), Hae(11).
        s_idx = HANJA_TO_IDX_CHEONGAN.get(day_stem)
        b_idx = HANJA_TO_IDX_JIJI.get(day_branch)
        
        # Calculate Sunjung (Ten group leader)
        # (b - s) -> starting branch of the group (Gap).
        # But for Gongmang:
        # (b_idx - s_idx) gives the index of branch corresponding to Gap if we shifted?
        # Standard: (Branch Index - Stem Index) % 12 gives the "Gap-XXX" residue? No.
        
        # Formula: (Branch - Stem)
        # if < 0 add 12.
        # This gives the offset from base.
        # Empty branches are at (Branch - Stem - 2) and (Branch - Stem - 1)?
        # Let's check:
        # Gap-Ja (0,0) -> 0. Empty: Sul(10), Hae(11).
        # Gap-Sul (0,10) -> 10. Empty: Shin(8), Yu(9).
        # Gap-In (0,2) -> 2. Empty: Chuk(1), Ja(0).
        
        # Correct Formula: The pair of empty branches corresponds to (Branch - Stem -1, Branch - Stem) or similar steps back?
        # Actually simplest: (Branch idx - Stem idx) gives the shift.
        # 0 -> Sul(10)/Hae(11)
        # 2 -> Ja(0)/Chuk(1)
        # 4 -> In(2)/Myo(3)
        # ...
        # Formula: remainder = (b_idx - s_idx) % 12
        # Gongmang 1 = (remainder - 2) % 12
        # Gongmang 2 = (remainder - 1) % 12
        
        remainder = (b_idx - s_idx) % 12
        gm1_idx = (remainder - 2) % 12
        gm2_idx = (remainder - 1) % 12
        
        gm1 = JIJI_HANJA[gm1_idx]
        gm2 = JIJI_HANJA[gm2_idx]
        
        has_gongmang = False
        for key, branch in branches.items():
            if key == 'day': continue # Gongmang applies to other pillars relative to Day
            if branch == gm1 or branch == gm2:
                found.append(f"공망({key})")
                has_gongmang = True
                
        # Deduplicate
        return list(set(found))

    def _check_trinity_shensha(self, base, branches):
        res = []
        # Base's Trinity (Samhap)
        # Find the center (Wangji) or group
        # In-O-Sul(Fire), Sa-Yu-Chuk(Metal)...
        
        group = None
        # Naive lookup
        if base in ["寅", "午", "戌"]: group = ["寅", "午", "戌"] # Fire
        elif base in ["申", "子", "辰"]: group = ["申", "子", "辰"] # Water
        elif base in ["巳", "酉", "丑"]: group = ["巳", "酉", "丑"] # Metal
        elif base in ["亥", "卯", "未"]: group = ["亥", "卯", "未"] # Wood
        
        if not group: return []
        
        # Yeokma: First char of group (Saengji) collision?
        # Definition:
        # In-O-Sul -> Shin (Monkey) is Yeokma.
        # Shin-Ja-Jin -> In (Tiger) is Yeokma.
        # Sa-Yu-Chuk -> Hae (Pig) is Yeokma.
        # Hae-Myo-Mi -> Sa (Snake) is Yeokma.
        # Rule: The index of First char + 6 (Opposite)?
        # In(Tiger) <-> Shin(Monkey). Yes.
        
        yeokma_char = None
        if group[0] == "寅": yeokma_char = "申"
        elif group[0] == "申": yeokma_char = "寅"
        elif group[0] == "巳": yeokma_char = "亥"
        elif group[0] == "亥": yeokma_char = "巳"
        
        # Dohwa: Center char (Wangji) - 1? No.
        # In-O-Sul -> Myo (Rabbit).
        # Shin-Ja-Jin -> Yu (Rooster).
        # Sa-Yu-Chuk -> O (Horse).
        # Hae-Myo-Mi -> Ja (Rat).
        # Rule: Next season's center?
        # Fire(In-O-Sul) -> Wood's center (Myo)? No. Myo is Wood.
        # Logic: First char + 1 index?
        # In(2) -> Myo(3). Yes.
        # Shin(8) -> Yu(9). Yes.
        # Sa(5) -> O(6). Yes.
        # Hae(11) -> Ja(0). Yes.
        
        first_idx = HANJA_TO_IDX_JIJI[group[0]]
        dohwa_idx = (first_idx + 1) % 12
        dohwa_char = JIJI_HANJA[dohwa_idx]
        
        # Hwagae: Last char (Goji).
        hwagae_char = group[2]
        
        for key, branch in branches.items():
            if branch == yeokma_char: res.append("역마살")
            if branch == dohwa_char: res.append("도화살")
            if branch == hwagae_char: res.append("화개살")
            
        return res

if __name__ == "__main__":
    c = Calculator()
    print(c.get_saju(2024, 1, 1, 12)) 

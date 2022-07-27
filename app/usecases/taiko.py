from math import floor

def taiko_mods(m: int) -> list[str]:
    mods = []
    valid = {
        "EZ": 2,
        "NF": 1,
        "HT": 256,

        "HR": 16,
        "DT": 64,
        "NC": 512,
        "HD": 8,
        "FL": 1024,
    }

    if (m & valid["NC"]) or (m & valid["DT"]):
        mods.append("DT")
        valid["NC"] = 0
        valid["DT"] = 0

    for mod in valid:
        if valid[mod] != 0 and (m & valid[mod]):
            mods.append(mod)
    
    return mods

class Taiko:
    def __init__(self, hitcount: int, misscount: int, od: float, acc: float):
        self.hitcount = hitcount
        self.misscount = misscount
        self.od = od
        self.acc = acc

    def modsOD(self, od: float, mods: list[str]):
        if "EZ" in mods:
            od /= 2.0
        elif "HR" in mods:
            od *= 1.4

        return max(min(od, 10), 0)

    def timingWindows(self, od: float, mods: list[str]):
        m_max, m_min = 20, 50
        results = floor(m_min + ((m_max - m_min) * self.modsOD(od, mods)) / 10) - 0.5

        if "HT" in mods:
            results /= 0.75
        elif "DT" in mods:
            results /= 1.5
        
        return round(results * 100) / 100

    def calculate(self, strain: float, bit_mods: int):
        mods = taiko_mods(bit_mods)
        OD300 = self.timingWindows(self.od, mods)
        combo = self.hitcount - self.misscount
        good = round(
            (1 - self.misscount / self.hitcount - self.acc / 100)
            * 2 * self.hitcount
        )

        if strain < 0 or self.hitcount < 0 or self.misscount < 0 or combo < 0 or self.acc < 0 or self.acc > 100 or OD300 < 0 or self.misscount + good > self.hitcount or good < 0:
            return 0.0
        
        strainamt = pow(max(1, strain / 0.0075) * 5 - 4, 2) / 100000
        length = min(1, self.hitcount / 1500) * 0.1 + 1

        strainamt *= length
        strainamt *= pow(0.985, self.misscount)
        strainamt *= min(
            pow(combo, 0.5) / pow(self.hitcount, 0.5), 1
        )
        strainamt *= self.acc / 100

        accamt = pow(150 / OD300, 1.1) * pow(self.acc / 100, 15) * 22
        modamt = 1.1

        accamt *= min(pow(self.hitcount / 1500, 0.3), 1.15)

        if "HD" in mods:
            modamt *= 1.1
            strainamt *= 1.025

        if "NF" in mods:
            modamt *= 0.9

        if "FL" in mods:
            strainamt *= 1.05 * length

        return round(
            pow(
                pow(strainamt, 1.1) + pow(accamt, 1.1),
                1.0 / 1.1
            ) * modamt * 100
        ) / 100

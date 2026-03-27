"""
Advanced Arabic text generators for inheritance problems.

Generates natural, diverse Arabic problem statements and detailed
Fiqh reasoning traces matching the original train data quality.
"""

import random
from typing import List, Dict, Any, Optional


# Arabic numerals - both word forms
ARABIC_NUMERALS = {
    1: ("واحد", "واحدة"),
    2: ("اثنان", "اثنتان"),
    3: ("ثلاثة", "ثلاث"),
    4: ("أربعة", "أربع"),
    5: ("خمسة", "خمس"),
    6: ("ستة", "ست"),
    7: ("سبعة", "سبع"),
    8: ("ثمانية", "ثمان"),
    9: ("تسعة", "تسع"),
    10: ("عشرة", "عشر"),
}

# Heir information with gender, plurals, and Fiqh descriptions
HEIR_INFO = {
    "زوج": {
        "gender": "M",
        "singular": "زوج",
        "dual": "زوجان",
        "plural": "أزواج",
        "fiqh_category": "الأزواج",
        "description": "الزوج من أصحاب الفروض",
    },
    "زوجة": {
        "gender": "F",
        "singular": "زوجة",
        "dual": "زوجتان",
        "plural": "زوجات",
        "fiqh_category": "الأزواج",
        "description": "الزوجة من أصحاب الفروض",
    },
    "ابن": {
        "gender": "M",
        "singular": "ابن",
        "dual": "ابنان",
        "plural": "أبناء",
        "fiqh_category": "الفروع الوارثة",
        "description": "الابن من العصبة بالنفس وهو أقوى الورثة",
    },
    "بنت": {
        "gender": "F",
        "singular": "بنت",
        "dual": "بنتان",
        "plural": "بنات",
        "fiqh_category": "الفروع الوارثة",
        "description": "البنت ترث بالفرض أو التعصيب",
    },
    "أب": {
        "gender": "M",
        "singular": "أب",
        "dual": "أبوان",
        "plural": "آباء",
        "fiqh_category": "الأصول الوارثة",
        "description": "الأب من أصحاب الفروض والعصبة معاً",
    },
    "أم": {
        "gender": "F",
        "singular": "أم",
        "dual": "أمان",
        "plural": "أمهات",
        "fiqh_category": "الأصول الوارثة",
        "description": "الأم من أصحاب الفروض",
    },
    "جد": {
        "gender": "M",
        "singular": "جد",
        "dual": "جدان",
        "plural": "أجداد",
        "fiqh_category": "الأصول الوارثة",
        "description": "الجد (أب الأب) من أصحاب الفروض والعصبة",
    },
    "أب الأب": {
        "gender": "M",
        "singular": "أب الأب",
        "dual": "أبوا الأب",
        "plural": "أجداد",
        "fiqh_category": "الأصول الوارثة",
        "description": "الجد الصحيح يرث كالجد",
    },
    "أب أب الأب": {
        "gender": "M",
        "singular": "أب أب الأب",
        "dual": "أبوا أب الأب",
        "plural": "أجداد",
        "fiqh_category": "الأصول الوارثة",
        "description": "والد الجد من الأصول الوارثة",
    },
    "أم الأم": {
        "gender": "F",
        "singular": "أم الأم",
        "dual": "أما الأم",
        "plural": "جدات",
        "fiqh_category": "الأصول الوارثة",
        "description": "الجدة الصحيحة من أصحاب الفروض",
    },
    "أم الأب": {
        "gender": "F",
        "singular": "أم الأب",
        "dual": "أما الأب",
        "plural": "جدات",
        "fiqh_category": "الأصول الوارثة",
        "description": "جدة من جهة الأب من أصحاب الفروض",
    },
    "أم أم الأم": {
        "gender": "F",
        "singular": "أم أم الأم",
        "dual": "أما أم الأم",
        "plural": "جدات",
        "fiqh_category": "الأصول الوارثة",
        "description": "الجدة البعيدة من جهة الأم",
    },
    "أم أم الأب": {
        "gender": "F",
        "singular": "أم أم الأب",
        "dual": "أما أم الأب",
        "plural": "جدات",
        "fiqh_category": "الأصول الوارثة",
        "description": "الجدة البعيدة من جهة الأب",
    },
    "أم أب الأب": {
        "gender": "F",
        "singular": "أم أب الأب",
        "dual": "أما أب الأب",
        "plural": "جدات",
        "fiqh_category": "الأصول الوارثة",
        "description": "جدة الأب من أصحاب الفروض",
    },
    "ابن ابن": {
        "gender": "M",
        "singular": "ابن ابن",
        "dual": "ابنا ابن",
        "plural": "أبناء ابن",
        "fiqh_category": "الفروع الوارثة",
        "description": "ابن الابن من العصبة بالنفس",
    },
    "بنت ابن": {
        "gender": "F",
        "singular": "بنت ابن",
        "dual": "بنتا ابن",
        "plural": "بنات ابن",
        "fiqh_category": "الفروع الوارثة",
        "description": "بنت الابن ترث بالفرض أو التعصيب",
    },
    "ابن ابن ابن": {
        "gender": "M",
        "singular": "ابن ابن ابن",
        "dual": "ابنا ابن ابن",
        "plural": "أبناء ابن ابن",
        "fiqh_category": "الفروع الوارثة",
        "description": "حفيد الابن من العصبة",
    },
    "بنت ابن ابن": {
        "gender": "F",
        "singular": "بنت ابن ابن",
        "dual": "بنتا ابن ابن",
        "plural": "بنات ابن ابن",
        "fiqh_category": "الفروع الوارثة",
        "description": "حفيدة الابن من الفروع الوارثة",
    },
    "أخ شقيق": {
        "gender": "M",
        "singular": "أخ شقيق",
        "dual": "أخوان شقيقان",
        "plural": "إخوة أشقاء",
        "fiqh_category": "الحواشي",
        "description": "الأخ الشقيق من العصبة بالنفس",
    },
    "أخت شقيقة": {
        "gender": "F",
        "singular": "أخت شقيقة",
        "dual": "أختان شقيقتان",
        "plural": "أخوات شقيقات",
        "fiqh_category": "الحواشي",
        "description": "الأخت الشقيقة من أصحاب الفروض أو عصبة مع الغير",
    },
    "أخ لأب": {
        "gender": "M",
        "singular": "أخ لأب",
        "dual": "أخوان لأب",
        "plural": "إخوة لأب",
        "fiqh_category": "الحواشي",
        "description": "الأخ لأب من العصبة بالنفس",
    },
    "أخت لأب": {
        "gender": "F",
        "singular": "أخت لأب",
        "dual": "أختان لأب",
        "plural": "أخوات لأب",
        "fiqh_category": "الحواشي",
        "description": "الأخت لأب من أصحاب الفروض",
    },
    "أخ لأم": {
        "gender": "M",
        "singular": "أخ لأم",
        "dual": "أخوان لأم",
        "plural": "إخوة لأم",
        "fiqh_category": "الحواشي",
        "description": "الأخ لأم من أصحاب الفروض",
    },
    "أخت لأم": {
        "gender": "F",
        "singular": "أخت لأم",
        "dual": "أختان لأم",
        "plural": "أخوات لأم",
        "fiqh_category": "الحواشي",
        "description": "الأخت لأم من أصحاب الفروض",
    },
    "ابن أخ شقيق": {
        "gender": "M",
        "singular": "ابن أخ شقيق",
        "dual": "ابنا أخ شقيق",
        "plural": "أبناء أخ شقيق",
        "fiqh_category": "الحواشي",
        "description": "ابن الأخ الشقيق من العصبة البعيدة",
    },
    "ابن أخ لأب": {
        "gender": "M",
        "singular": "ابن أخ لأب",
        "dual": "ابنا أخ لأب",
        "plural": "أبناء أخ لأب",
        "fiqh_category": "الحواشي",
        "description": "ابن الأخ لأب من العصبة",
    },
    "ابن ابن أخ شقيق": {
        "gender": "M",
        "singular": "ابن ابن أخ شقيق",
        "dual": "ابنا ابن أخ شقيق",
        "plural": "أبناء ابن أخ شقيق",
        "fiqh_category": "الحواشي",
        "description": "حفيد الأخ الشقيق من العصبة",
    },
    "عم شقيق": {
        "gender": "M",
        "singular": "عم شقيق",
        "dual": "عمان شقيقان",
        "plural": "أعمام أشقاء",
        "fiqh_category": "الأعمام",
        "description": "العم الشقيق من العصبة",
    },
    "عم لأب": {
        "gender": "M",
        "singular": "عم لأب",
        "dual": "عمان لأب",
        "plural": "أعمام لأب",
        "fiqh_category": "الأعمام",
        "description": "العم لأب من العصبة",
    },
    "عم الأب": {
        "gender": "M",
        "singular": "عم الأب",
        "dual": "عما الأب",
        "plural": "أعمام الأب",
        "fiqh_category": "الأعمام",
        "description": "عم الأب من العصبة البعيدة",
    },
    "عم الأب لأب": {
        "gender": "M",
        "singular": "عم الأب لأب",
        "dual": "عما الأب لأب",
        "plural": "أعمام الأب لأب",
        "fiqh_category": "الأعمام",
        "description": "عم الأب لأب من العصبة البعيدة",
    },
    "ابن عم شقيق": {
        "gender": "M",
        "singular": "ابن عم شقيق",
        "dual": "ابنا عم شقيق",
        "plural": "أبناء عم شقيق",
        "fiqh_category": "الأعمام",
        "description": "ابن العم الشقيق من العصبة البعيدة",
    },
    "ابن عم لأب": {
        "gender": "M",
        "singular": "ابن عم لأب",
        "dual": "ابنا عم لأب",
        "plural": "أبناء عم لأب",
        "fiqh_category": "الأعمام",
        "description": "ابن العم لأب من العصبة",
    },
    "ابن عم الأب": {
        "gender": "M",
        "singular": "ابن عم الأب",
        "dual": "ابنا عم الأب",
        "plural": "أبناء عم الأب",
        "fiqh_category": "الأعمام",
        "description": "ابن عم الأب من العصبة البعيدة",
    },
    "ابن ابن عم شقيق": {
        "gender": "M",
        "singular": "ابن ابن عم شقيق",
        "dual": "ابنا ابن عم شقيق",
        "plural": "أبناء ابن عم شقيق",
        "fiqh_category": "الأعمام",
        "description": "حفيد العم الشقيق من العصبة",
    },
    "ابن ابن عم لأب": {
        "gender": "M",
        "singular": "ابن ابن عم لأب",
        "dual": "ابنا ابن عم لأب",
        "plural": "أبناء ابن عم لأب",
        "fiqh_category": "الأعمام",
        "description": "حفيد العم لأب من العصبة",
    },
}

# Question opening phrases - very diverse
QUESTION_OPENINGS = [
    "مات وترك:",
    "توفي وترك:",
    "هلك رجل عن:",
    "توفيت امرأة وخلّفت:",
    "مات رجل تاركاً:",
    "توفي شخص وخلّف من بعده:",
    "انتقل إلى رحمة الله تاركاً:",
    "توفي إلى رحمة الله وترك:",
    "مات شخص وورثه:",
    "توفي رجل عن ورثة هم:",
]

# Question endings - very diverse
QUESTION_ENDINGS = [
    "ما هو نصيب كل وريث؟",
    "ما هو نصيب كل وارث؟",
    "كيف تقسم التركة؟",
    "كيف توزع التركة بينهم؟",
    "ما نصيب كل منهم؟",
    "قسّم الميراث بينهم.",
    "وزّع التركة عليهم.",
    "ما حصة كل وارث من التركة؟",
    "أوجد نصيب كل وارث.",
    "بيّن نصيب كل منهم من الميراث.",
    "حدد الورثة وأنصبتهم.",
    "ما هي حصة كل وارث شرعاً؟",
]

# Share names in Arabic
SHARE_NAMES = {
    "1/2": "النصف",
    "1/4": "الربع",
    "1/8": "الثمن",
    "2/3": "الثلثان",
    "1/3": "الثلث",
    "1/6": "السدس",
}

# Blocking reasons in detailed Arabic
BLOCKING_REASONS = {
    "ابن": "بوجود الابن الذي يحجبه حجب حرمان",
    "ابن ابن": "بوجود الابن أو ابن الابن الأعلى درجة",
    "بنت ابن": "بوجود الابن الذي يحجبها",
    "أخ شقيق": "بوجود الفرع الوارث الذكر أو الأب",
    "أخت شقيقة": "بوجود الفرع الوارث الذكر أو الأب",
    "أخ لأب": "بوجود الأخ الشقيق أو الفرع الوارث الذكر أو الأب",
    "أخت لأب": "بوجود الأخ الشقيق أو الأختين الشقيقتين فأكثر",
    "أخ لأم": "بوجود الفرع الوارث مطلقاً أو الأصل الذكر",
    "أخت لأم": "بوجود الفرع الوارث مطلقاً أو الأصل الذكر",
    "جد": "بوجود الأب الذي يحجبه",
    "أب الأب": "بوجود الأب الذي يحجبه",
    "أم الأم": "بوجود الأم التي تحجبها",
    "أم الأب": "بوجود الأم التي تحجبها",
    "عم شقيق": "بوجود الأب أو الجد أو الإخوة الأقرب",
    "عم لأب": "بوجود العم الشقيق أو من هو أقرب",
    "ابن أخ شقيق": "بوجود الإخوة أو من هو أقرب في العصوبة",
    "ابن أخ لأب": "بوجود ابن الأخ الشقيق أو من هو أقرب",
    "ابن عم شقيق": "بوجود الأعمام أو أبناء الإخوة",
    "ابن عم لأب": "بوجود ابن العم الشقيق أو من هو أقرب",
}


class ArabicProblemGenerator:
    """Generate diverse Arabic problem texts for inheritance cases."""
    
    def generate(self, heirs: List[Dict]) -> str:
        """Generate a natural Arabic problem statement."""
        opening = random.choice(QUESTION_OPENINGS)
        ending = random.choice(QUESTION_ENDINGS)
        heirs_list = self._format_heirs_diverse(heirs)
        
        # Add some variation in structure
        style = random.choice(["standard", "with_و", "comma_separated"])
        
        if style == "standard":
            return f"{opening} {heirs_list}. {ending}"
        elif style == "with_و":
            return f"{opening} {heirs_list} {ending}"
        else:
            return f"{opening} {heirs_list}، {ending}"
    
    def _format_heirs_diverse(self, heirs: List[Dict]) -> str:
        """Format heir list with Arabic variety."""
        parts = []
        
        for h in heirs:
            heir_type = h.get("heir", "")
            count = h.get("count", 1)
            
            info = HEIR_INFO.get(heir_type, {})
            is_female = info.get("gender", "M") == "F"
            
            if count == 1:
                parts.append(info.get("singular", heir_type))
            elif count == 2:
                parts.append(info.get("dual", heir_type))
            else:
                # Use number + plural with gender agreement
                num_forms = ARABIC_NUMERALS.get(count, (str(count), str(count)))
                num = num_forms[1] if is_female else num_forms[0]
                plural = info.get("plural", heir_type)
                parts.append(f"{num} {plural}")
        
        # Shuffle for variety
        random.shuffle(parts)
        
        # Join with varied connectors
        if len(parts) == 0:
            return "لا ورثة"
        elif len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            connector = random.choice(["و", " و "])
            return f"{parts[0]} {connector}{parts[1]}"
        else:
            # Use و for last item, و or comma for others
            result = parts[0]
            for i, p in enumerate(parts[1:-1], 1):
                sep = random.choice([" و ", "، و", " و", "،"])
                result += f"{sep}{p}"
            result += f" و{parts[-1]}"
            return result


class ArabicReasoningGenerator:
    """Generate detailed Fiqh reasoning traces matching original train data."""
    
    def generate(
        self,
        input_heirs: List[Dict],
        shares: List[Dict],
        blocked: List[Dict],
        result: Any
    ) -> str:
        """Generate comprehensive reasoning trace in Arabic."""
        sections = []
        
        # Opening statement
        sections.append(self._intro())
        
        # Section 1: Identify heirs and blocking
        sections.append(self._section_heirs_and_blocking(input_heirs, blocked))
        
        # Section 2: Eligible heirs summary
        sections.append(self._section_eligible_heirs(shares))
        
        # Section 3: Determine shares
        sections.append(self._section_shares(shares))
        
        # Section 4: Base calculation
        sections.append(self._section_base(result))
        
        # Section 5: Correction if needed
        sections.append(self._section_correction(result))
        
        return "\n\n".join(sections)
    
    def _intro(self) -> str:
        """Generate intro paragraph."""
        intros = [
            "لحل هذه المسألة في المواريث، أبدأ بتحليل المعطيات لتحديد الورثة الشرعيين ومن يحجب منهم، ثم أحدد نصيب كل وارث خطوة بخطوة.",
            "لحل مسألة الميراث هذه، نحتاج أولاً إلى تحديد الورثة الشرعيين، ثم تطبيق قواعد الحجب، وأخيراً توزيع التركة.",
            "سأقوم بحل هذه المسألة وفقاً لأحكام الميراث الشرعية، مع بيان من يرث ومن يُحجب ونصيب كل وارث.",
            "نبدأ بتحليل هذه المسألة الإرثية بتحديد أصناف الورثة وتطبيق قواعد الحجب والتوريث.",
        ]
        return random.choice(intros)
    
    def _section_heirs_and_blocking(self, input_heirs: List[Dict], blocked: List[Dict]) -> str:
        """Section 1: Detailed heir analysis with blocking."""
        lines = ["**1. تحديد الورثة الشرعيين ومن يحجب:**"]
        lines.append("المتوفى ترك:")
        
        blocked_types = {b["heir"] for b in blocked}
        
        for h in input_heirs:
            heir_type = h.get("heir", "")
            count = h.get("count", 1)
            info = HEIR_INFO.get(heir_type, {})
            
            if count == 1:
                heir_name = info.get("singular", heir_type)
            else:
                heir_name = f"{heir_type} ({count} أفراد)"
            
            lines.append(f"*   **{heir_name}:** {info.get('description', '')}")
            
            if heir_type in blocked_types:
                reason = BLOCKING_REASONS.get(heir_type, "بوجود وارث أقرب")
                lines.append(f"    - **محجوب** {reason}.")
        
        return "\n".join(lines)
    
    def _section_eligible_heirs(self, shares: List[Dict]) -> str:
        """Section: Summary of eligible heirs."""
        lines = ["**خلاصة الورثة الفعليين:**"]
        lines.append("الورثة الشرعيون هم:")
        
        for i, s in enumerate(shares, 1):
            heir_type = s.get("heir", "")
            count = s.get("count", 1)
            info = HEIR_INFO.get(heir_type, {})
            
            if count == 1:
                lines.append(f"{i}.  {info.get('singular', heir_type)}.")
            else:
                lines.append(f"{i}.  {info.get('plural', heir_type)} ({count} أفراد).")
        
        return "\n".join(lines)
    
    def _section_shares(self, shares: List[Dict]) -> str:
        """Section: Determine shares with Fiqh reasoning."""
        lines = ["**2. تحديد فروض وأنصبة الورثة:**"]
        
        for s in shares:
            heir_type = s.get("heir", "")
            count = s.get("count", 1)
            fraction = s.get("fraction", "")
            info = HEIR_INFO.get(heir_type, {})
            
            if count == 1:
                heir_name = info.get("singular", heir_type)
            else:
                heir_name = f"{info.get('plural', heir_type)} ({count} أفراد)"
            
            share_name = SHARE_NAMES.get(fraction, fraction)
            reason = self._get_share_reason(heir_type, fraction)
            
            lines.append(f"*   **{heir_name}:** {share_name} ({fraction}) {reason}")
        
        return "\n".join(lines)
    
    def _get_share_reason(self, heir_type: str, fraction: str) -> str:
        """Get Fiqh reason for share."""
        reasons = {
            ("زوج", "1/2"): "لعدم وجود الفرع الوارث.",
            ("زوج", "1/4"): "لوجود الفرع الوارث.",
            ("زوجة", "1/4"): "لعدم وجود الفرع الوارث.",
            ("زوجة", "1/8"): "لوجود الفرع الوارث.",
            ("أم", "1/3"): "لعدم وجود الفرع الوارث ولا جمع من الإخوة.",
            ("أم", "1/6"): "لوجود الفرع الوارث أو جمع من الإخوة.",
            ("أب", "1/6"): "لوجود الفرع الوارث.",
            ("بنت", "1/2"): "لانفرادها وعدم وجود المعصّب.",
            ("بنت", "2/3"): "لتعددهن وعدم وجود المعصّب.",
            ("أخت شقيقة", "1/2"): "لانفرادها وعدم وجود المعصّب.",
            ("أخت شقيقة", "2/3"): "لتعددهن وعدم وجود المعصّب.",
            ("أخت شقيقة", "باقى التركة"): "عصبة مع الغير لوجود الفرع الوارث المؤنث.",
            ("أخت لأب", "1/6"): "تكملة الثلثين مع الأخت الشقيقة.",
            ("أخ لأم", "1/6"): "لانفراده.",
            ("أخت لأم", "1/6"): "لانفرادها.",
            ("جد", "1/6"): "لوجود الفرع الوارث.",
        }
        return reasons.get((heir_type, fraction), "فرضاً أو تعصيباً حسب الحال.")
    
    def _section_base(self, result: Any) -> str:
        """Section: Base calculation."""
        lines = ["**3. أصل المسألة وتوزيع السهام:**"]
        
        tasil = result.tasil_stage if hasattr(result, 'tasil_stage') else {}
        base = tasil.get("asl", 1) if isinstance(tasil, dict) else 1
        
        lines.append(f"أصل المسألة: **{base}**")
        
        # Add distribution if available
        dist = tasil.get("distribution", []) if isinstance(tasil, dict) else []
        if dist:
            lines.append("توزيع السهام:")
            for d in dist:
                heir = d.get("heir", "")
                shares_val = d.get("shares", "")
                lines.append(f"*   {heir}: {shares_val}")
        
        return "\n".join(lines)
    
    def _section_correction(self, result: Any) -> str:
        """Section: Awl/Radd/Tashih."""
        lines = ["**4. التصحيح:**"]
        
        awl_or_radd = result.awl_or_radd if hasattr(result, 'awl_or_radd') else "لا"
        
        if awl_or_radd == "لا":
            lines.append("المسألة صحيحة ولا تحتاج إلى عول أو رد.")
        elif awl_or_radd == "عول":
            lines.append("المسألة عائلة، أي أن مجموع الفروض يتجاوز الواحد الصحيح.")
            lines.append("يتم تقليص الأنصبة بنسبة متساوية لتتناسب مع التركة.")
        elif awl_or_radd == "رد":
            lines.append("المسألة فيها رد، حيث لم تستغرق الفروض كامل التركة ولا يوجد عاصب.")
            lines.append("يُرد الباقي على أصحاب الفروض عدا الزوجين.")
        
        return "\n".join(lines)


# ── Share reasons for NL answer generator ───────────────────────────────────
SHARE_REASONS = {
    ("زوج", "1/2"): "لعدم وجود الفرع الوارث فللزوج النصف.",
    ("زوج", "1/4"): "لوجود الفرع الوارث فللزوج الربع.",
    ("زوجة", "1/4"): "لعدم وجود الفرع الوارث فللزوجة الربع.",
    ("زوجة", "1/8"): "لوجود الفرع الوارث فللزوجة الثمن.",
    ("أم", "1/3"): "لعدم وجود الفرع الوارث ولا جمع من الإخوة فللأم الثلث.",
    ("أم", "1/6"): "لوجود الفرع الوارث أو جمعٍ من الإخوة فللأم السدس.",
    ("أب", "1/6"): "لوجود الفرع الوارث فللأب السدس فرضاً.",
    ("جد", "1/6"): "للجد السدس فرضاً لوجود الفرع الوارث.",
    ("أب الأب", "1/6"): "للجد السدس فرضاً لوجود الفرع الوارث.",
    ("بنت", "1/2"): "لانفرادها وعدم وجود ابن يعصّبها فللبنت الواحدة النصف.",
    ("بنت", "2/3"): "لتعددها وعدم وجود المعصّب فلهن الثلثان.",
    ("أخت شقيقة", "1/2"): "لانفرادها وعدم وجود المعصّب فلها النصف.",
    ("أخت شقيقة", "2/3"): "لتعددها وعدم وجود المعصّب فلهن الثلثان.",
    ("أخت شقيقة", "باقى التركة"): "عصبة مع الغير لوجود الفرع الوارث المؤنث.",
    ("أخت لأب", "1/6"): "تكملة الثلثين مع الأخت الشقيقة.",
    ("أخ لأم", "1/6"): "لانفراده فله السدس.",
    ("أخت لأم", "1/6"): "لانفرادها فلها السدس.",
}


def _heir_name_nl(heir_type: str, count: int) -> str:
    """Return correctly inflected Arabic heir name for the given count (for NL answers)."""
    info = HEIR_INFO.get(heir_type, {})
    if count == 1:
        return info.get("singular", heir_type)
    if count == 2:
        return info.get("dual", heir_type)
    num_pair = ARABIC_NUMERALS.get(count, (str(count), str(count)))
    is_female = info.get("gender", "M") == "F"
    num_word = num_pair[1] if is_female else num_pair[0]
    plural = info.get("plural", heir_type)
    return f"{num_word} {plural}"


# ── NL Answer Templates ──────────────────────────────────────────────────────

_NL_ANSWER_INTROS = [
    "بناءً على قواعد المواريث في الشريعة الإسلامية، يتم تقسيم التركة كالتالي:",
    "وفقاً لأحكام الفرائض في الشريعة الإسلامية، توزّع التركة على النحو الآتي:",
    "بتطبيق أحكام المواريث الشرعية، تُقسَّم التركة كما يلي:",
    "حسب قواعد علم الفرائض، يكون توزيع الميراث كالتالي:",
    "استناداً إلى الأحكام الشرعية للمواريث، تكون القسمة على النحو التالي:",
]

_NL_SHARE_TEMPLATES = [
    "- {name}: {reason_with_share}",
    "- {name}: له/لها {share_ar} ({frac})؛ {reason}",
    "- {name}: نصيبه/نصيبها {share_ar} ({frac})، {reason}",
    "- {name}: يرث/ترث {share_ar} ({frac})، {reason}",
]

_NL_ASABA_TEMPLATES = [
    "- {name}: عصبة بالنفس، يرث الباقي تعصيباً.",
    "- {name}: يأخذ الباقي بعد أصحاب الفروض تعصيباً بالنفس.",
    "- {name}: له الباقي تعصيباً بعد توزيع الفروض.",
]

_NL_ASABA_WITH_FEMALE_TEMPLATES = [
    "- {name}: عصبة مع الغير، يأخذ/تأخذ الباقي تعصيباً.",
    "- {name}: يرث/ترث الباقي بالتعصيب مع الغير.",
]

_NL_BLOCKED_TEMPLATES = [
    "- {name}: محجوب/محجوبة {reason}، فلا يرث/لا ترث.",
    "- {name}: لا شيء له/لها (محجوب/محجوبة) {reason}.",
    "- {name}: محجوب/محجوبة حجب حرمان {reason}، فلا نصيب له/لها.",
]

_NL_BASE_TEMPLATES = [
    "أصل المسألة من ({base}):",
    "أصل المسألة: ({base}).",
]

_NL_AWL_NOTES = [
    "المسألة عائلة، فيُضم الزائد إلى الأصل ويتحمل كل وارث النقص بالتناسب.",
    "عالت المسألة، إذ تجاوز مجموع الفروض الواحد الصحيح، فتُخفَّض الحصص بالتناسب.",
]

_NL_RADD_NOTES = [
    "المسألة فيها رد: الباقي بعد الفروض يُردّ على أصحاب الفروض (عدا الزوجين) بنسبة فروضهم.",
    "بقي من التركة فضل بعد الفروض، فيُردّ على الورثة المستحقين للرد بتناسب أنصبتهم.",
]


class ArabicNLAnswerGenerator:
    """
    Generate diverse natural-language Q&A text for inheritance problems.

    Produces a `qa_nl` string in the format:
        السؤال:
        <question text>

        الجواب:
        <natural-language answer with heir shares, blocked heirs, base, etc.>
    """

    def __init__(self, rng: Optional[random.Random] = None):
        self._rng = rng or random.Random()

    def generate(
        self,
        problem_text: str,
        shares: List[Dict],
        blocked: List[Dict],
        result: Any,
    ) -> str:
        """Generate a full QA string in natural Arabic."""
        sections = [
            self._section_question(problem_text),
            self._section_answer(shares, blocked, result),
        ]
        return "\n\n".join(sections)

    def _section_question(self, problem_text: str) -> str:
        return f"السؤال:\n{problem_text}"

    def _section_answer(
        self, shares: List[Dict], blocked: List[Dict], result: Any
    ) -> str:
        lines = ["الجواب:"]
        lines.append(self._rng.choice(_NL_ANSWER_INTROS))

        for s in shares:
            lines.append(self._format_share_line(s))

        for b in blocked:
            lines.append(self._format_blocked_line(b))

        awl_note = self._format_awl_radd(result)
        if awl_note:
            lines.append("")
            lines.append(awl_note)

        base_section = self._format_base_section(result)
        if base_section:
            lines.append("")
            lines.append(base_section)

        return "\n".join(lines)

    def _format_share_line(self, share: Dict) -> str:
        heir = share["heir"]
        count = share["count"]
        frac = share.get("fraction", "")
        name = _heir_name_nl(heir, count)

        if frac in ("باقي التركة", "باقى التركة", "الباقي", "عصبة"):
            if heir in ("أخت شقيقة", "أخت لأب"):
                tpl = self._rng.choice(_NL_ASABA_WITH_FEMALE_TEMPLATES)
            else:
                tpl = self._rng.choice(_NL_ASABA_TEMPLATES)
            return tpl.format(name=name)

        share_ar = SHARE_NAMES.get(frac, frac)
        reason = self._get_brief_reason(heir, frac, count)

        style = self._rng.randint(0, len(_NL_SHARE_TEMPLATES) - 1)
        if style == 0:
            reason_with_share = f"له/لها {share_ar} ({frac}) {reason}"
            return _NL_SHARE_TEMPLATES[0].format(
                name=name, reason_with_share=reason_with_share
            )
        else:
            tpl = _NL_SHARE_TEMPLATES[style]
            return tpl.format(
                name=name, share_ar=share_ar, frac=frac, reason=reason
            )

    def _format_blocked_line(self, blocked: Dict) -> str:
        heir = blocked["heir"]
        count = blocked.get("count", 1)
        name = _heir_name_nl(heir, count)
        reason = BLOCKING_REASONS.get(heir, "بوجود وارث أقرب منه")
        tpl = self._rng.choice(_NL_BLOCKED_TEMPLATES)
        return tpl.format(name=name, reason=reason)

    def _format_awl_radd(self, result: Any) -> str:
        awr = getattr(result, "awl_or_radd", "لا")
        if awr == "عول":
            return self._rng.choice(_NL_AWL_NOTES)
        elif awr == "رد":
            return self._rng.choice(_NL_RADD_NOTES)
        return ""

    def _format_base_section(self, result: Any) -> str:
        post = getattr(result, "post_tasil", None) or {}
        if not isinstance(post, dict):
            return ""
        dist = post.get("distribution", [])
        total = post.get("total_shares", 0)
        if not dist or not total:
            return ""

        lines = [self._rng.choice(_NL_BASE_TEMPLATES).format(base=total)]
        for d in dist:
            heir = d.get("heir", "")
            count = d.get("count", 1)
            name = _heir_name_nl(heir, count)
            per_head = d.get("per_head_shares", "")
            pct = d.get("per_head_percent", 0)
            pct_str = f"{pct:.2f}%" if isinstance(pct, float) else str(pct)
            lines.append(f"    {name}: {per_head} ({pct_str})")

        return "\n".join(lines)

    def _get_brief_reason(self, heir: str, frac: str, count: int) -> str:
        r = SHARE_REASONS.get((heir, frac))
        if r:
            return r
        return "فرضاً وفق قواعد الفرائض."

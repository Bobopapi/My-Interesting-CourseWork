from dataclasses import dataclass

@dataclass
class LocaleGroup():
    tab_value: str
    tab_name: str
    content_title: str
    # Reflex gives an error if I try to pass in a list of LocaleItem. Appearently its JSON serialization issues and there is no known fix.
    # Handle accordingly in the state classes instead.
    # items: list[LocaleItem]

@dataclass
class LocaleItem():
    id: int
    name: str
    description: str

    def __eq__(self, other):
        if not isinstance(other, LocaleItem):
            return False
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
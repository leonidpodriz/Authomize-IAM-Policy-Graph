def get_unique_identifier_from_name(name: str) -> str:
    return '/'.join(name.split('/')[-2:])


def get_resource_object_type(asset_type: str) -> str:
    return asset_type.split('/')[-1]


def get_edge_type(previous_type: str, next_type: str) -> str:
    return f'{previous_type.title()}To{next_type.title()}'
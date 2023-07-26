from st_aggrid import AgGrid, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode
from st_aggrid.grid_options_builder import GridOptionsBuilder


class GridBuilder:

    dados: str
    key: str
    sel_mode: str

    def __init__(self, data, key, selmode="multiple", updatemode=GridUpdateMode.MANUAL, returnmode=DataReturnMode.FILTERED_AND_SORTED):
        """AgGrid Component creation

        Args:
            data (_type_): data that will be used to build the aggrid components
            key (_type_): identifies the aggrid component
            updatemode (_type_, optional): how the data will be updated after filtering it. Defaults to GridUpdateMode.MANUAL.
            selmode (str, optional): the selection mode. Defaults to "multiple".
            returnmode (_type_, optional): how the data will be returned after filtering it. Defaults to GridUpdateMode.MANUAL. Defaults to DataReturnMode.FILTERED_AND_SORTED.
        """

        self.data = data
        self.grid_key = key
        self.sel_mode = selmode
        self.updatemode = updatemode
        self.returnmode = returnmode
        self.gdoptions = self.config_builder()

    def config_builder(self):

        gd_builder = GridOptionsBuilder.from_dataframe(self.data)

        gd_builder.configure_pagination(enabled=True)
        gd_builder.configure_default_column(editable=True, groupable=True,
                                            filterable=True, resizable=True
                                            )

        gd_builder.configure_selection(selection_mode=self.sel_mode, use_checkbox=True, header_checkbox_filtered_only=True,
                                       suppressRowDeselection=True, suppressRowClickSelection=False,
                                       rowMultiSelectWithClick=False, header_checkbox=True
                                       )

        gd_options = gd_builder.build()

        return gd_options

    def grid_builder(self, height=500, display_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW):
        if display_mode == 'FIT_CONTENTS':
            display_mode = ColumnsAutoSizeMode.FIT_CONTENTS
        custom_css = {
            ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "13px",
            "font-family": "Roboto, sans-serif !important;", "text-align":"center"},
            ".ag-header-cell-label": {"justify-content": "center;"},
            ".ag-theme-light button": {"font-size": "0 !important;", "width": "auto !important;", "height": "24px !important;"},
            ".ag-theme-light button:before": {"content": "'Confirm' !important", "position": "relative !important;"}
        }
        tab = AgGrid(self.data, gridOptions=self.gdoptions,
                     theme="balham", key=self.grid_key, height=height,
                     update_mode=self.updatemode, data_return_mode=DataReturnMode.FILTERED_AND_SORTED, allow_unsafe_jscode=True,
                     columns_auto_size_mode=display_mode, custom_css=custom_css)

        return tab, tab.data
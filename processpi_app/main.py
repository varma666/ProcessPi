import flet as ft

def main(page: ft.Page):
    page.title = "ProcessPI - Flowsheet GUI"
    page.bgcolor = "#f0f0f0"
    page.horizontal_alignment = "stretch"
    page.vertical_alignment = "stretch"

    blocks = []

    # ----- Menubar -----
    menubar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("ProcessPI", size=20, weight="bold", color="#333333"),
                ft.Text("File", color="#555555"),
                ft.Text("Edit", color="#555555"),
                ft.Text("View", color="#555555"),
                ft.Text("Help", color="#555555"),
            ],
            alignment="spaceBetween",
            expand=True,
        ),
        bgcolor="#e0e0e0",
        padding=10,
    )

    # ----- Status Bar -----
    statusbar = ft.Container(
        content=ft.Text("Ready", color="#333333"),
        bgcolor="#e0e0e0",
        height=30,
        alignment=ft.alignment.center_left,
        padding=10,
    )

    # ----- Properties Panel -----
    properties_panel = ft.Column(
        controls=[
            ft.Text("Properties", weight="bold", color="#333333"),
            ft.TextField(label="Pressure (P)", width=150),
            ft.TextField(label="Temperature (T)", width=150),
            ft.TextField(label="Flow Rate", width=150),
        ],
        spacing=10,
    )

    # ----- Flowsheet Canvas -----
    flowsheet_canvas = ft.Stack(expand=True)

    # Helper functions
    def on_block_click(block_container):
        # Update properties panel with block data
        page.controls[2].controls[1].value = block_container.data.get("P", "")
        page.controls[2].controls[2].value = block_container.data.get("T", "")
        page.controls[2].controls[3].value = block_container.data.get("flow", "")
        page.update()

    def move_block(block_container, dx, dy):
        block_container.position["x"] += dx
        block_container.position["y"] += dy
        page.update()

    def add_block(block_name):
        block_container = ft.Container(
            content=ft.Text(block_name),
            bgcolor="#cccccc",
            width=120,
            height=60,
            alignment=ft.alignment.center,
            border=ft.border.all(1, "#999999"),
        )
        block_container.data = {"P": "", "T": "", "flow": ""}
        block_container.position = {"x": 50, "y": 50 + len(blocks) * 80}

        block = ft.GestureDetector(
            content=block_container,
            on_tap=lambda e: on_block_click(block_container),
            on_pan_update=lambda e: move_block(block_container, e.delta_x, e.delta_y),
        )

        blocks.append(block)
        flowsheet_canvas.controls.append(
            ft.Positioned(
                left=block_container.position["x"],
                top=block_container.position["y"],
                content=block
            )
        )
        page.update()

    # ----- Sidebar / Model Library -----
    sidebar = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Model Library", weight="bold", color="#333333"),
                ft.ElevatedButton("Pump", on_click=lambda e: add_block("Pump")),
                ft.ElevatedButton("Compressor", on_click=lambda e: add_block("Compressor")),
                ft.ElevatedButton("Heat Exchanger", on_click=lambda e: add_block("Heat Exchanger")),
                ft.ElevatedButton("Reactor", on_click=lambda e: add_block("Reactor")),
                ft.ElevatedButton("Separator", on_click=lambda e: add_block("Separator")),
                ft.Divider(),
                ft.Text("Properties Panel", weight="bold", color="#333333"),
                properties_panel
            ],
            spacing=10,
        ),
        bgcolor="#f8f8f8",
        border=ft.border.all(1, "#cccccc"),
        width=250,
        padding=10,
    )

    # ----- Main Layout -----
    layout = ft.Column(
        controls=[
            menubar,
            ft.Row(
                controls=[sidebar, flowsheet_canvas],
                expand=True,
            ),
            statusbar,
        ],
        expand=True,
    )

    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)

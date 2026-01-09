import sqlite3

class ShipmentProcessor:
    def __init__(self, db_path):
        self.db_path = db_path

    def process_shipment(self, item_name, quantity, log_callback):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        log_callback(f"--- STARTING TRANSACTION: Move {quantity} of {item_name} ---")

        try:
            
            cursor.execute("BEGIN") 
            cursor.execute(
                "UPDATE inventory SET stock_qty = stock_qty - ? WHERE item_name = ?",
                (quantity, item_name)
            )
            log_callback(">> STEP 1 SUCCESS: Inventory Deducted.")

            cursor.execute(
                "INSERT INTO shipment_log (item_name, qty_moved) VALUES (?, ?)",
                (item_name, quantity)
            )
            log_callback(">> STEP 2 SUCCESS: Shipment Logged.")

            conn.commit()
            log_callback("--- TRANSACTION COMMITTED ---")

        except sqlite3.IntegrityError as e:
            # If Step 1 fails, rollback => Step 2 is not saved
            conn.rollback()
            log_callback(f">> TRANSACTION FAILED (ROLLBACK): {e}")

        except Exception as e:
            # Any other error: rollback as well
            conn.rollback()
            log_callback(f">> TRANSACTION FAILED (ROLLBACK): {e}")

        finally:
            conn.close()

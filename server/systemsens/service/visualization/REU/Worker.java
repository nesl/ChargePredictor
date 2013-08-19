import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Date;

public class Worker {
  private Connection connect = null;
  private Statement statement = null;
  private ResultSet resultSet = null;

  public void readDataBase(String imei, String json_tree_diagram) throws Exception {
    try {
      Class.forName("com.mysql.jdbc.Driver");
      connect = DriverManager
          .getConnection("jdbc:mysql://localhost/service?"
              + "user=root&password=neslrocks!");

      statement = connect.createStatement();
      statement
          .executeUpdate("UPDATE user_models SET model='" + json_tree_diagram + "' WHERE imei=" + imei + ";");
      System.out.println("Wrote to database.");

    } catch (Exception e) {
      throw e;
    } finally {
      close();
    }

  }

  // You need to close the resultSet
  private void close() {
    try {
      if (resultSet != null) {
        resultSet.close();
      }

      if (statement != null) {
        statement.close();
      }

      if (connect != null) {
        connect.close();
      }
    } catch (Exception e) {

    }
  }

} 
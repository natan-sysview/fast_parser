import java.awt.BorderLayout;
import java.awt.Dimension;
import javax.swing.AbstractAction;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.SwingUtilities;
import javax.swing.Timer;
import javax.swing.table.DefaultTableModel;

public class SwingShowcase extends JFrame {
  private final JButton saveButton = new JButton("Save");
  private final JTable usersTable = new JTable();
  private final DefaultTableModel usersModel = new DefaultTableModel();

  public SwingShowcase() {
    initComponents();
  }

  private void initComponents() {
    JPanel content = new JPanel(new BorderLayout());
    usersModel.addColumn("Name");
    usersModel.addRow(new Object[] { "Sample" });
    usersTable.setModel(usersModel);
    usersTable.setPreferredScrollableViewportSize(new Dimension(400, 120));

    saveButton.addActionListener(event -> JOptionPane.showMessageDialog(this, "Saved"));

    JMenuBar menuBar = new JMenuBar();
    JMenu fileMenu = new JMenu("File");
    fileMenu.add(new JMenuItem(new AbstractAction("Exit") {
      @Override
      public void actionPerformed(java.awt.event.ActionEvent event) {
        setVisible(false);
      }
    }));
    menuBar.add(fileMenu);
    setJMenuBar(menuBar);

    content.add(new JScrollPane(usersTable), BorderLayout.CENTER);
    content.add(saveButton, BorderLayout.SOUTH);
    setContentPane(content);
    setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
    pack();

    new Timer(1000, event -> saveButton.requestFocusInWindow()).start();
  }

  public static void main(String[] args) {
    SwingUtilities.invokeLater(() -> new SwingShowcase().setVisible(true));
  }
}

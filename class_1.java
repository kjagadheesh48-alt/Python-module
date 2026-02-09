class Student {
    public int roll_no;
    public String name;

    Student(int roll_no, String name) {
        this.roll_no = roll_no;
        this.name = name;
    }
}

public class class_1 {
    public static void main(String[] args) {

        Student[] arr;          // FIXED HERE
        arr = new Student[5];

        arr[0] = new Student(1, "John");
        arr[1] = new Student(2, "Jane");
        arr[2] = new Student(3, "Bob");
        arr[3] = new Student(4, "Alice");
        arr[4] = new Student(5, "Charlie");

        for (int i = 0; i < arr.length; i++) {
            System.out.println(
                "Roll No: " + arr[i].roll_no + ", Name: " + arr[i].name
            );
        }
    }
}

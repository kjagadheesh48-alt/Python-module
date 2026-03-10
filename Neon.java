import java.util.Scanner;
public class Neon{
    public static boolean checkNeon(int n)  {
        Scanner sc = new Scanner(System.in);
        System.out.print("Enter a number: ");
        int num = sc.nextInt();
        int square = num * num;
        int sum = 0;
        
        while (square > 0) {
            sum += square % 10;
            square /= 10;
        }
        return sum==n;
    }
    public static void main(String[] args) {
        int n = 9; // Example number to check
        if (checkNeon(n)) {
            System.out.println(n + " is a Neon number.");
        } else {
            System.out.println(n + " is not a Neon number.");
        }
    }
}